#!/usr/bin/env python3
"""Consolidate committed candidate mappings; read no research refs or evidence files."""

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = "docs/external-stage/stage-candidate-matrix.json"
BATCH_PATHS = tuple(f"docs/external-stage/mapping-decisions-batch{number}.json" for number in range(1, 6))
RESOLUTION_PATH = "docs/external-stage/cold-evidence-mapping-resolutions.json"
INPUT_PATHS = (MATRIX_PATH, *BATCH_PATHS, RESOLUTION_PATH)
OUTPUT = REPO_ROOT / "docs/external-stage/resolved-stage-candidates.json"
DISPOSITIONS = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NEEDS_COLD_EVIDENCE"}
FINAL_OUTCOMES = (DISPOSITIONS - {"NEEDS_COLD_EVIDENCE"}) | {"NOT_INDEPENDENT_PARAMETER", "STILL_UNRESOLVED"}
SHAPES = {"VANILLA_REUSE", "PRIMITIVE_COMPOSITION", "CUSTOM_SPECIAL", "NON_SCALAR"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    return {path: json.loads((REPO_ROOT / path).read_bytes()) for path in INPUT_PATHS}


def compile_registry(sources):
    require(set(sources) == set(INPUT_PATHS), "Use exactly the seven committed mapping inputs")
    matrix = sources[MATRIX_PATH]
    by_id = {}
    legacy_keys = set()
    for mechanic in matrix["mechanics"]:
        mechanic_id = mechanic["mechanic_id"]
        require(mechanic_id not in by_id, f"Duplicate mechanic: {mechanic_id}")
        by_id[mechanic_id] = mechanic
        for candidate in mechanic["scalable_parameter_candidates"]:
            if candidate["candidate_form"] == "LEGACY_UNSCOPED":
                key = (mechanic_id, candidate["candidate_name"])
                require(key not in legacy_keys, f"Duplicate legacy candidate: {key}")
                legacy_keys.add(key)

    reviews = {}
    for path in BATCH_PATHS:
        for mechanic in sources[path]["mechanics"]:
            original = by_id[mechanic["mechanic_id"]]
            for field in ("mod_key", "primary_classification"):
                require(mechanic[field] == original[field], f"Review mechanic mismatch: {field}")
            for decision in mechanic["decisions"]:
                key = (mechanic["mechanic_id"], decision["candidate_name"])
                require(key not in reviews, f"Duplicate reviewed candidate: {key}")
                require(decision["disposition"] in DISPOSITIONS, f"Unknown disposition: {key}")
                require(decision["integration_shape"] in SHAPES, f"Unknown integration shape: {key}")
                require(decision["confidence"] in {"HIGH", "MEDIUM", "LOW"}, f"Unknown confidence: {key}")
                reviews[key] = (path, decision)
    require(set(reviews) == legacy_keys, "Reviewed decisions must cover every legacy candidate exactly once")

    cold = {}
    for resolution in sources[RESOLUTION_PATH]["resolutions"]:
        key = (resolution["mechanic_id"], resolution["candidate_name"])
        require(key not in cold and key in reviews, f"Duplicate or orphan cold resolution: {key}")
        path, previous = reviews[key]
        require(resolution["previous_batch"] == path, f"Wrong previous batch: {key}")
        require(resolution["previous_disposition"] == previous["disposition"] == "NEEDS_COLD_EVIDENCE", f"Wrong previous disposition: {key}")
        require(resolution["final_outcome"] in FINAL_OUTCOMES, f"Unknown final outcome: {key}")
        require(resolution["confidence"] in {"HIGH", "MEDIUM", "LOW"}, f"Unknown cold confidence: {key}")
        cold[key] = resolution
    require(set(cold) == {key for key, (_, decision) in reviews.items() if decision["disposition"] == "NEEDS_COLD_EVIDENCE"}, "Every cold-evidence decision needs exactly one resolution")

    mechanics = []
    for mechanic in matrix["mechanics"]:
        record = {field: deepcopy(value) for field, value in mechanic.items() if field != "scalable_parameter_candidates"}
        primitives = {component["primitive"] for component in mechanic.get("components") or []}
        entries = []
        for candidate in mechanic["scalable_parameter_candidates"]:
            form = candidate["candidate_form"]
            if form in {"STRUCTURED", "RECOVERED_EXACT"}:
                parameters = candidate["parameters"]
                require(isinstance(parameters, list) and parameters and all(isinstance(p, str) and p for p in parameters), "Expected nonempty parameter names")
                require(len(parameters) == len(set(parameters)), "Duplicate structured parameter")
                require(candidate["needs_mapping_review"] is False, "Scoped mapping still needs review")
                for parameter in parameters:
                    entry = {
                        "candidate_name": candidate.get("candidate_name", parameter),
                        "parameter": parameter,
                        "disposition": "MAP_EXISTING_COMPONENT",
                        "primitive": candidate["primitive"],
                        "integration_shape": candidate.get("integration_shape"),
                        "confidence": candidate.get("confidence"),
                        "independent_runtime_parameter": True,
                        "mapping_reason": "Existing structured primitive/parameter mapping preserved." if form == "STRUCTURED" else "Existing exact component numerical-parameter key mapping preserved.",
                        "provenance": {"kind": form, "source": MATRIX_PATH},
                    }
                    if "meaning" in candidate:
                        entry["meaning"] = deepcopy(candidate["meaning"])
                    if "recovery" in candidate:
                        entry["provenance"]["recovery"] = deepcopy(candidate["recovery"])
                    entries.append(entry)
            else:
                require(form == "LEGACY_UNSCOPED", f"Unknown candidate form: {form}")
                key = (mechanic["mechanic_id"], candidate["candidate_name"])
                path, decision = reviews[key]
                effective = cold.get(key, decision)
                outcome = effective.get("final_outcome", effective.get("disposition"))
                entry = {
                    "candidate_name": candidate["candidate_name"],
                    "parameter": decision["candidate_parameter"],
                    "disposition": outcome,
                    "integration_shape": decision["integration_shape"],
                    "confidence": effective["confidence"],
                    "independent_runtime_parameter": outcome != "NOT_INDEPENDENT_PARAMETER",
                    "mapping_reason": effective["reason"],
                    "provenance": {"kind": "SEMANTIC_REVIEW", "source": path},
                }
                if outcome == "MAP_EXISTING_COMPONENT":
                    entry["primitive"] = effective["target_primitive"]
                if key in cold:
                    entry["provenance"] = {"kind": "COLD_EVIDENCE_RESOLUTION", "source": RESOLUTION_PATH, "semantic_review": path, "previous_disposition": decision["disposition"], "evidence": deepcopy(effective["evidence"])}
                if outcome == "NOT_INDEPENDENT_PARAMETER":
                    require(effective.get("existing_parameters"), f"Alias has no real parameters: {key}")
                    entry["superseded_by"] = deepcopy(effective["existing_parameters"])
                entries.append(entry)
        require(entries, f"Mechanic has no candidates: {mechanic['mechanic_id']}")
        identities = [(entry.get("primitive"), entry["candidate_name"], entry["parameter"]) for entry in entries]
        require(len(identities) == len(set(identities)), f"Duplicate registry candidate: {mechanic['mechanic_id']}")
        for entry in entries:
            if entry["disposition"] == "MAP_EXISTING_COMPONENT":
                require(entry["primitive"] in primitives, f"Missing existing primitive: {entry['primitive']}")
            for parameter in entry.get("superseded_by", []):
                require(any(other.get("primitive") == parameter["primitive"] and other["parameter"] == parameter["parameter"] and other["independent_runtime_parameter"] for other in entries), "Alias replacement is not an existing independent candidate")
        record["candidates"] = sorted(entries, key=lambda entry: (entry.get("primitive", ""), entry["parameter"], entry["candidate_name"]))
        mechanics.append(record)
    mechanics.sort(key=lambda record: (record["mod_key"], record["mechanic_id"]))
    entries = [entry for mechanic in mechanics for entry in mechanic["candidates"]]
    unresolved = sum(entry["disposition"] in {"NEEDS_COLD_EVIDENCE", "STILL_UNRESOLVED"} for entry in entries)
    require(unresolved == 0, "Cannot publish a resolved registry with unresolved mappings")
    return {
        "schema_version": 1,
        "source_files": list(INPUT_PATHS),
        "registry_scope": "Mapping consolidation only; no Stage eligibility or policy decision. Null shape/confidence means the original mapping did not supply it. Independent counts are per candidate entry, not unique runtime boundaries.",
        "summary": {
            "total_candidate_mechanics": len(mechanics),
            "total_candidate_entries": len(entries),
            "independent_runtime_parameter_count": sum(entry["independent_runtime_parameter"] for entry in entries),
            "not_independent_parameter_count": sum(not entry["independent_runtime_parameter"] for entry in entries),
            "counts_by_integration_shape": dict(sorted(Counter(entry["integration_shape"] or "UNSPECIFIED" for entry in entries).items())),
            "counts_by_disposition": dict(sorted(Counter(entry["disposition"] for entry in entries).items())),
            "counts_by_provenance": dict(sorted(Counter(entry["provenance"]["kind"] for entry in entries).items())),
            "reviewed_decision_count": len(reviews),
            "cold_evidence_resolution_count": len(cold),
            "unresolved_count": unresolved,
        },
        "mechanics": mechanics,
    }


def serialize_registry(registry):
    """Keep one compact mechanic per line; omit timestamps and host-specific paths."""
    metadata = {key: value for key, value in registry.items() if key != "mechanics"}
    header = json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)[:-2]
    body = ",\n".join("    " + json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for record in registry["mechanics"])
    return (header + ',\n  "mechanics": [\n' + body + '\n  ]\n}\n').encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        registry = compile_registry(load_inputs())
        payload = serialize_registry(registry)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {registry['summary']['total_candidate_entries']} candidates across {len(registry['mechanics'])} mechanics to {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Normalize existing Stage candidates using only the committed integration manifest."""

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = "docs/external-stage/integration-manifest.json"
INPUT = REPO_ROOT / SOURCE_PATH
OUTPUT = REPO_ROOT / "docs/external-stage/stage-candidate-matrix.json"
RECORD_FIELDS = (
    "mod_key", "mechanic_id", "primary_classification", "stage_review_bucket",
    "closest_vanilla_equivalent",
)


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize_candidate(candidate, primitives):
    if isinstance(candidate, str):
        return {
            "candidate_name": candidate,
            "candidate_form": "LEGACY_UNSCOPED",
            "needs_mapping_review": True,
            "available_component_primitives": primitives,
        }
    if (isinstance(candidate, dict) and isinstance(candidate.get("primitive"), str)
            and isinstance(candidate.get("parameters"), list)
            and all(isinstance(parameter, str) for parameter in candidate["parameters"])):
        result = deepcopy(candidate)
        result["parameters"] = sorted(candidate["parameters"])
        result["candidate_form"] = "STRUCTURED"
        result["needs_mapping_review"] = False
        return result
    raise ValueError("Unsupported candidate shape; primitive ownership must not be guessed")


def candidate_sort_key(candidate):
    if candidate["candidate_form"] == "STRUCTURED":
        return (0, candidate["primitive"], tuple(candidate["parameters"]), canonical_json(candidate))
    return (1, candidate["candidate_name"], (), canonical_json(candidate))


def normalize_mechanic(mechanic):
    components = mechanic.get("components") or []
    primitives = sorted({component["primitive"] for component in components if "primitive" in component})
    candidates = sorted(
        (normalize_candidate(candidate, primitives) for candidate in mechanic["scalable_parameter_candidates"]),
        key=candidate_sort_key,
    )
    result = {field: deepcopy(mechanic[field]) for field in RECORD_FIELDS if field in mechanic}
    if "components" in mechanic:
        if mechanic["components"] is None:
            result["components"] = None
        else:
            # Legacy names have no owner mapping: every source component remains review context.
            legacy = any(candidate["candidate_form"] == "LEGACY_UNSCOPED" for candidate in candidates)
            scoped = {candidate["primitive"] for candidate in candidates if candidate["candidate_form"] == "STRUCTURED"}
            relevant = [component for component in components if legacy or component.get("primitive") in scoped]
            result["components"] = sorted(deepcopy(relevant), key=lambda component: (component.get("primitive", ""), canonical_json(component)))
    result["scalable_parameter_candidates"] = candidates
    return result


def compile_matrix(manifest):
    records = []
    identities = set()
    for mechanic in manifest["mechanics"]:
        identity = (mechanic["mod_key"], mechanic["mechanic_id"])
        if identity in identities:
            raise ValueError(f"Duplicate manifest mechanic identity: {identity}")
        identities.add(identity)
        candidates = mechanic.get("scalable_parameter_candidates")
        if candidates:
            if not isinstance(candidates, list):
                raise ValueError(f"Expected a candidate list: {identity}")
            records.append(normalize_mechanic(mechanic))
    records.sort(key=lambda record: (record["mod_key"], record["mechanic_id"]))
    structured = legacy = parameter_count = 0
    pairs = set()
    for record in records:
        for candidate in record["scalable_parameter_candidates"]:
            if candidate["candidate_form"] == "STRUCTURED":
                structured += 1
                parameter_count += len(candidate["parameters"])
                pairs.update((candidate["primitive"], parameter) for parameter in candidate["parameters"])
            else:
                legacy += 1
    return {
        "schema_version": 1,
        "source_manifest": SOURCE_PATH,
        "summary": {
            "total_mechanics": len(manifest["mechanics"]),
            "mechanics_with_stage_candidates": len(records),
            "structured_candidate_count": structured,
            "structured_parameter_count": parameter_count,
            "legacy_unscoped_candidate_count": legacy,
            "unique_structured_pair_count": len(pairs),
            "unique_structured_pairs": [{"primitive": primitive, "parameter": parameter} for primitive, parameter in sorted(pairs)],
            "counts_by_mod": dict(sorted(Counter(record["mod_key"] for record in records).items())),
            "counts_by_stage_review_bucket": dict(sorted(Counter(record["stage_review_bucket"] for record in records).items())),
        },
        "mechanics": records,
    }


def serialize_matrix(matrix):
    """Emit standard JSON with one compact mechanic per line, without timestamps."""
    metadata = {key: value for key, value in matrix.items() if key != "mechanics"}
    header = json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)[:-2]
    body = ",\n".join("    " + canonical_json(record) for record in matrix["mechanics"])
    return (header + ',\n  "mechanics": [\n' + body + '\n  ]\n}\n').encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        matrix = compile_matrix(json.loads(INPUT.read_bytes()))
        payload = serialize_matrix(matrix)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {len(matrix['mechanics'])} candidate-bearing mechanics to {args.output}")


if __name__ == "__main__":
    main()

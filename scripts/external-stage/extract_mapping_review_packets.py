#!/usr/bin/env python3
"""Compact unresolved mapping context without resolving or interpreting any candidate."""

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess

import extract_candidate_matrix as matrix_extractor


INPUT = matrix_extractor.OUTPUT
OUTPUT = matrix_extractor.REPO_ROOT / "docs/external-stage/mapping-review-packets.json"
SOURCE_REF = "external-effects-catalog-research"
REVIEW_PATHS = {
    mod: f"docs/benchmarks/external-effects-catalog/mod-reviews/{mod}.json"
    for mod in ("cultofazazel", "twilightforest", "variantsandventures")
}
TEXT_LIMIT = 240
RECORD_FIELDS = (
    "display_name", "primary_classification", "closest_vanilla_equivalent",
    "actual_behavior", "vanilla_differences", "numerical_parameters",
    "binary_parameters", "scalability_note",
)
COMPONENT_FIELDS = ("primitive", "formula", "numerical_parameters", "binary_parameters", "vanilla_relation")
CANDIDATE_FIELDS = ("candidate_name", "reason", "matching_primitives")


def compact_value(value):
    """Bound string leaves by source-prefix excerpts; retain keys and non-text facts."""
    if isinstance(value, str):
        text = " ".join(value.split())
        if len(text) <= TEXT_LIMIT:
            return text
        prefix = text[:TEXT_LIMIT - 1]
        if " " in prefix:
            prefix = prefix.rsplit(" ", 1)[0]
        return prefix.rstrip() + "…"
    if isinstance(value, list):
        return [compact_value(item) for item in value]
    if isinstance(value, dict):
        return {key: compact_value(item) for key, item in value.items()}
    return value


def unresolved_mechanics(matrix):
    records = []
    identities = set()
    for mechanic in matrix["mechanics"]:
        if not any(candidate.get("needs_mapping_review") is True for candidate in mechanic["scalable_parameter_candidates"]):
            continue
        identity = (mechanic["mod_key"], mechanic["mechanic_id"])
        if identity[0] not in REVIEW_PATHS:
            raise ValueError(f"Unresolved mod review is not allowlisted: {identity[0]}")
        if identity in identities:
            raise ValueError(f"Duplicate unresolved mechanic identity: {identity}")
        identities.add(identity)
        records.append(mechanic)
    return sorted(records, key=lambda record: (record["mod_key"], record["mechanic_id"]))


def read_sources(matrix, ref=SOURCE_REF):
    records = unresolved_mechanics(matrix)
    commit = None
    for candidate in (ref, f"refs/remotes/origin/{ref}"):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{candidate}^{{commit}}"],
            cwd=matrix_extractor.REPO_ROOT, capture_output=True, text=True,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()
            break
    if commit is None:
        raise ValueError(f"Cannot resolve {ref}; fetch the research ref without checking it out")
    matrix_commit = matrix.get("mapping_recovery_source", {}).get("source_commit")
    if matrix_commit is not None and matrix_commit != commit:
        raise ValueError("Packet source commit must match the matrix recovery snapshot")
    sources = {}
    review_bytes = record_bytes = 0
    paths = []
    for mod in sorted({record["mod_key"] for record in records}):
        path = REVIEW_PATHS[mod]
        raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=matrix_extractor.REPO_ROOT, stderr=subprocess.PIPE)
        review = json.loads(raw)
        if review.get("status") != "COMPLETE" or review.get("mod_key") != mod:
            raise ValueError(f"Not the expected completed review: {path}")
        paths.append(path)
        review_bytes += len(raw)
        for record in records:
            if record["mod_key"] != mod:
                continue
            matching = [source for source in review["effects"] if source["id"] == record["mechanic_id"]]
            if len(matching) != 1 or matching[0].get("mod_key") != mod:
                raise ValueError(f"Expected one exact source mechanic: {mod} / {record['mechanic_id']}")
            source = matching[0]
            record_bytes += len(matrix_extractor.canonical_json(source).encode("utf-8"))
            # Only the requested context fields leave the reader; all audit material stays cold.
            projection = {field: source[field] for field in RECORD_FIELDS if field in source}
            if "components" in source:
                projection["components"] = None if source["components"] is None else [
                    {field: component[field] for field in COMPONENT_FIELDS if field in component}
                    for component in source["components"]
                ]
            sources[(mod, record["mechanic_id"])] = projection
    return sources, {
        "source_ref": SOURCE_REF, "source_commit": commit, "source_reviews": sorted(paths),
        "source_review_bytes": review_bytes, "selected_source_record_bytes": record_bytes,
    }


def compile_packets(matrix, sources, provenance):
    packets = []
    for mechanic in unresolved_mechanics(matrix):
        identity = (mechanic["mod_key"], mechanic["mechanic_id"])
        if identity not in sources:
            raise ValueError(f"Missing exact source mechanic: {identity}")
        source = sources[identity]
        packet = {"mod_key": identity[0], "mechanic_id": identity[1]}
        packet.update({field: compact_value(source[field]) for field in RECORD_FIELDS if field in source})
        if "components" in source:
            packet["components"] = None if source["components"] is None else [
                {field: compact_value(component[field]) for field in COMPONENT_FIELDS if field in component}
                for component in source["components"]
            ]
        candidates = []
        for candidate in mechanic["scalable_parameter_candidates"]:
            if candidate.get("needs_mapping_review") is not True:
                continue
            if not isinstance(candidate.get("candidate_name"), str) or not isinstance(candidate.get("reason"), str):
                raise ValueError(f"Cannot guess an unresolved candidate name or reason: {identity}")
            candidates.append({field: deepcopy(candidate[field]) for field in CANDIDATE_FIELDS if field in candidate})
        packet["unresolved_candidates"] = sorted(candidates, key=lambda candidate: (candidate["candidate_name"], matrix_extractor.canonical_json(candidate)))
        packets.append(packet)
    return {
        "schema_version": 1,
        "source_matrix": "docs/external-stage/stage-candidate-matrix.json",
        **provenance,
        "text_excerpt_limit": TEXT_LIMIT,
        "summary": {
            "total_unresolved_mechanics": len(packets),
            "total_unresolved_candidates": sum(len(packet["unresolved_candidates"]) for packet in packets),
            "counts_by_mod": dict(sorted(Counter(packet["mod_key"] for packet in packets).items())),
            "counts_by_unresolved_reason": dict(sorted(Counter(candidate["reason"] for packet in packets for candidate in packet["unresolved_candidates"]).items())),
        },
        "mechanics": packets,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=SOURCE_REF, help="Research ref or its pinned review commit")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        matrix = json.loads(INPUT.read_bytes())
        sources, provenance = read_sources(matrix, args.ref)
        packets = compile_packets(matrix, sources, provenance)
        payload = matrix_extractor.serialize_matrix(packets)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {len(packets['mechanics'])} mechanic packets ({len(payload)} bytes)")


if __name__ == "__main__":
    main()

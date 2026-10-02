#!/usr/bin/env python3
"""Recover legacy matrix mappings only from exact component numerical-parameter keys."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess

import extract_candidate_matrix as matrix_extractor


INPUT = matrix_extractor.OUTPUT
SOURCE_REF = "external-effects-catalog-research"
REVIEW_PATHS = {
    mod: f"docs/benchmarks/external-effects-catalog/mod-reviews/{mod}.json"
    for mod in ("cultofazazel", "twilightforest", "variantsandventures")
}
NUMERIC_FIELDS = ("numerical_parameters", "component_numerical_parameters")
RECOVERY_METHOD = "EXACT_COMPONENT_NUMERICAL_PARAMETER_KEY_MATCH"


def parameter_matches(mechanic, name):
    """Count components, not containers or distinct primitive names. Never inspect values."""
    indexed = mechanic.get("component_numerical_parameters") or {}
    if not isinstance(indexed, dict):
        raise ValueError("Unsupported indexed component numerical-parameter container")
    matches = []
    for index, component in enumerate(mechanic.get("components") or []):
        primitive = component["primitive"]
        if not isinstance(primitive, str) or not primitive:
            raise ValueError("A source component needs an explicit primitive")
        containers = [(f"components[{index}].{field}", component.get(field) or {}) for field in NUMERIC_FIELDS]
        indexed_key = f"{index}:{primitive}"
        containers.append((f"component_numerical_parameters[{indexed_key}]", indexed.get(indexed_key) or {}))
        key_sources = []
        for path, parameters in containers:
            if not isinstance(parameters, dict):
                raise ValueError(f"Unsupported component numerical-parameter container: {path}")
            if name in parameters:
                key_sources.append(path)
        if key_sources:
            matches.append({"primitive": primitive, "component_index": index, "key_sources": sorted(key_sources)})
    return matches


def read_legacy_reviews(matrix, ref=SOURCE_REF):
    """Git object reads of only allowlisted reviews and projection of exact legacy IDs."""
    requested = {}
    for mechanic in matrix["mechanics"]:
        if any(candidate["candidate_form"] == "LEGACY_UNSCOPED" for candidate in mechanic["scalable_parameter_candidates"]):
            mod = mechanic["mod_key"]
            if mod not in REVIEW_PATHS:
                raise ValueError(f"Legacy mod review is not allowlisted: {mod}")
            requested.setdefault(mod, set()).add(mechanic["mechanic_id"])
    previous = matrix.get("mapping_recovery_source")
    if not requested:
        return {}, deepcopy(previous)
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
    if previous and previous["source_commit"] != commit:
        raise ValueError("Existing recovered mappings use a different source commit; do not mix recovery snapshots")
    sources = {}
    for mod in sorted(requested):
        path = REVIEW_PATHS[mod]
        review = json.loads(subprocess.check_output(
            ["git", "show", f"{commit}:{path}"], cwd=matrix_extractor.REPO_ROOT, stderr=subprocess.PIPE,
        ))
        if review.get("status") != "COMPLETE" or review.get("mod_key") != mod:
            raise ValueError(f"Not the expected completed review: {path}")
        for mechanic_id in sorted(requested[mod]):
            matching = [mechanic for mechanic in review["effects"] if mechanic["id"] == mechanic_id]
            if len(matching) != 1 or matching[0].get("mod_key") != mod:
                raise ValueError(f"Expected one exact source mechanic: {mod} / {mechanic_id}")
            source = matching[0]
            # Only these component identity/numerical fields enter the recovery step.
            projection = {
                "components": [{field: component[field] for field in ("primitive", *NUMERIC_FIELDS) if field in component}
                               for component in source.get("components") or []],
            }
            if "component_numerical_parameters" in source:
                projection["component_numerical_parameters"] = source["component_numerical_parameters"]
            sources[(mod, mechanic_id)] = (path, projection)
    paths = {REVIEW_PATHS[mod] for mod in requested}
    if previous:
        paths.update(previous["review_files"])
    if not paths <= set(REVIEW_PATHS.values()):
        raise ValueError("Recovery provenance contains a non-allowlisted review")
    return sources, {"source_ref": SOURCE_REF, "source_commit": commit, "review_files": sorted(paths)}


def recover_candidate(candidate, path, source):
    result = deepcopy(candidate)
    name = candidate["candidate_name"]
    if not isinstance(name, str):
        raise ValueError("Legacy candidate name must be preserved as a string")
    for field in ("reason", "matching_primitives", "primitive", "parameters", "recovery"):
        result.pop(field, None)
    matches = parameter_matches(source, name)
    if len(matches) == 1:
        result.update({
            "candidate_form": "RECOVERED_EXACT", "needs_mapping_review": False,
            "primitive": matches[0]["primitive"], "parameters": [name],
            "recovery": {"method": RECOVERY_METHOD, "source_review": path,
                         "component_index": matches[0]["component_index"], "key_sources": matches[0]["key_sources"]},
        })
    else:
        result["needs_mapping_review"] = True
        result["reason"] = "NO_EXACT_COMPONENT_MATCH" if not matches else "AMBIGUOUS_COMPONENT_MATCH"
        if matches:
            result["matching_primitives"] = sorted(match["primitive"] for match in matches)
    return result


def candidate_sort_key(candidate):
    if candidate["candidate_form"] in ("STRUCTURED", "RECOVERED_EXACT"):
        return (0, candidate["primitive"], tuple(candidate["parameters"]), matrix_extractor.canonical_json(candidate))
    return (1, candidate["candidate_name"], (), matrix_extractor.canonical_json(candidate))


def recover_matrix(matrix, sources, provenance):
    result = deepcopy(matrix)
    identities = set()
    for mechanic in result["mechanics"]:
        identity = (mechanic["mod_key"], mechanic["mechanic_id"])
        if identity in identities:
            raise ValueError(f"Duplicate matrix mechanic identity: {identity}")
        identities.add(identity)
        recovered = []
        for candidate in mechanic["scalable_parameter_candidates"]:
            if candidate["candidate_form"] == "LEGACY_UNSCOPED":
                if identity not in sources:
                    raise ValueError(f"Missing exact source mechanic: {identity}")
                path, source = sources[identity]
                candidate = recover_candidate(candidate, path, source)
            elif candidate["candidate_form"] not in ("STRUCTURED", "RECOVERED_EXACT"):
                raise ValueError(f"Unsupported candidate form: {candidate['candidate_form']}")
            recovered.append(candidate)
        mechanic["scalable_parameter_candidates"] = sorted(recovered, key=candidate_sort_key)
    result["mechanics"].sort(key=lambda mechanic: (mechanic["mod_key"], mechanic["mechanic_id"]))
    candidates = [candidate for mechanic in result["mechanics"] for candidate in mechanic["scalable_parameter_candidates"]]
    original = sum(candidate["candidate_form"] == "STRUCTURED" for candidate in candidates)
    exact = sum(candidate["candidate_form"] == "RECOVERED_EXACT" for candidate in candidates)
    no_match = sum(candidate.get("reason") == "NO_EXACT_COMPONENT_MATCH" for candidate in candidates)
    ambiguous = sum(candidate.get("reason") == "AMBIGUOUS_COMPONENT_MATCH" for candidate in candidates)
    result["summary"].update({
        "original_structured_candidate_count": original,
        "recovered_exact_candidate_count": exact,
        "unresolved_no_match_candidate_count": no_match,
        "unresolved_ambiguous_candidate_count": ambiguous,
        "legacy_unscoped_candidate_count": no_match + ambiguous,
        "mechanics_needing_mapping_review_count": sum(any(candidate["needs_mapping_review"] for candidate in mechanic["scalable_parameter_candidates"]) for mechanic in result["mechanics"]),
    })
    result["schema_version"] = 2
    if provenance is not None:
        result["mapping_recovery_source"] = deepcopy(provenance)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=SOURCE_REF, help="Research ref or its pinned review commit")
    parser.add_argument("--output", type=Path, default=INPUT)
    args = parser.parse_args()
    try:
        matrix = json.loads(INPUT.read_bytes())
        sources, provenance = read_legacy_reviews(matrix, args.ref)
        result = recover_matrix(matrix, sources, provenance)
        payload = matrix_extractor.serialize_matrix(result)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Recovered {result['summary']['recovered_exact_candidate_count']} exact candidate mappings")


if __name__ == "__main__":
    main()

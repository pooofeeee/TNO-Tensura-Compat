#!/usr/bin/env python3
"""Project the nine completed static reviews into a compact routing manifest."""

import argparse
import json
from pathlib import Path
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_REF = "external-effects-catalog-research"
REVIEW_FILES = tuple(
    f"docs/benchmarks/external-effects-catalog/mod-reviews/{name}.json"
    for name in (
        "royalvariations", "cultofazazel", "variantsandventures", "friendsandfoes",
        "twilightforest", "iceandfire", "eternalstarlight", "block_factorys_bosses",
        "bosses_of_mass_destruction",
    )
)
OUTPUT = REPO_ROOT / "docs/external-stage/integration-manifest.json"
EXCERPT_LIMIT = 240
RECORD_FIELDS = (
    "display_name", "closest_vanilla_equivalent", "delivery_paths",
    "primary_test_source", "alternate_sources", "inspection_status", "unresolved_ambiguities",
)
COMPONENT_FIELDS = ("primitive", "attribute", "operation", "coefficient")
BUCKETS = {
    "VANILLA_DIRECT": "VANILLA_REUSE_CANDIDATE",
    "VANILLA_EQUIVALENT": "VANILLA_REUSE_CANDIDATE",
    "VANILLA_COMPOSITE": "PRIMITIVE_COMPOSITION_CANDIDATE",
    "VANILLA_LIKE_EXTENDED": "PRIMITIVE_COMPOSITION_CANDIDATE",
    "BINARY_MECHANIC": "NON_SCALAR_OR_SPECIAL_REVIEW",
}


def stage_review_bucket(classification):
    if isinstance(classification, str) and classification.startswith("CUSTOM_"):
        return "CUSTOM_POLICY_REVIEW"
    return BUCKETS.get(classification, "UNCLASSIFIED_REVIEW") if isinstance(classification, str) else "UNCLASSIFIED_REVIEW"


def excerpt(text):
    """Keep short source prose; otherwise quote its first sentence/prefix, marked with an ellipsis."""
    if text is None:
        return None
    if not isinstance(text, str):
        raise ValueError("Expected source prose to be a string or null")
    text = " ".join(text.split())
    if len(text) <= EXCERPT_LIMIT:
        return text
    prefix = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    if len(prefix) >= EXCERPT_LIMIT:
        prefix = prefix[:EXCERPT_LIMIT - 1]
        if " " in prefix:
            prefix = prefix.rsplit(" ", 1)[0]
    return prefix.rstrip() + "…"


def reduce_component(component):
    result = {key: component[key] for key in COMPONENT_FIELDS if key in component}
    numeric = component.get("numerical_parameters") or {}
    # Explicitly named numeric fields are source facts; never parse formulas or infer coefficients.
    if "coefficient" not in result and "coefficient" in numeric:
        result["coefficient"] = numeric["coefficient"]
    if "formula" in numeric:
        result["formula"] = excerpt(numeric["formula"])
    elif "formula" in component:
        result["formula"] = excerpt(component["formula"])
    return result


def reduce_differences(differences):
    """Normalize source notes/nested lists or explicit component native relations."""
    if differences is None:
        return None
    if isinstance(differences, str):
        return [excerpt(differences)]
    if isinstance(differences, list):
        result = []
        for item in differences:
            reduced = reduce_differences(item)
            result.extend([None] if reduced is None else reduced)
        return result
    if isinstance(differences, dict) and "component_contracts" in differences:
        return [excerpt(component.get("native_relation")) for component in differences["component_contracts"]]
    raise ValueError("Unsupported source vanilla_differences shape")


def reduce_mechanic(mechanic):
    for key in ("mod_key", "id"):
        if not isinstance(mechanic.get(key), str) or not mechanic[key]:
            raise ValueError(f"Cannot represent a mechanic without its source {key}")
    classification = mechanic.get("primary_classification")
    result = {
        "mod_key": mechanic["mod_key"],
        "mechanic_id": mechanic["id"],
        "primary_classification": classification,
        "stage_review_bucket": stage_review_bucket(classification),
    }
    result.update({key: mechanic[key] for key in RECORD_FIELDS if key in mechanic})
    if "vanilla_differences" in mechanic:
        result["vanilla_differences"] = reduce_differences(mechanic["vanilla_differences"])
    if "components" in mechanic:
        components = mechanic["components"]
        result["components"] = None if components is None else [reduce_component(component) for component in components]
    # These older review schemas name the same observed candidate list scalable_parameters.
    for key in ("scalable_parameter_candidates", "scalable_parameters"):
        if key in mechanic:
            result["scalable_parameter_candidates"] = mechanic[key]
            break
    return result


def resolve_ref(repo, ref):
    for candidate in (ref, f"refs/remotes/origin/{ref}"):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{candidate}^{{commit}}"],
            cwd=repo, capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    raise ValueError(f"Cannot resolve {ref}; fetch the research ref without checking it out")


def read_reviews(repo, ref):
    commit = resolve_ref(repo, ref)
    reviews = []
    for path in REVIEW_FILES:
        raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo, stderr=subprocess.PIPE)
        reviews.append((path, json.loads(raw)))
    return commit, reviews


def compile_manifest(reviews, commit, source_ref=SOURCE_REF):
    by_path = dict(reviews)
    if len(reviews) != len(REVIEW_FILES) or set(by_path) != set(REVIEW_FILES):
        raise ValueError("Exactly the nine allowlisted completed reviews are required")
    records = []
    identities = set()
    for path in REVIEW_FILES:
        review = by_path[path]
        if review.get("status") != "COMPLETE":
            raise ValueError(f"Review is not complete: {path}")
        for mechanic in review["effects"]:
            record = reduce_mechanic(mechanic)
            if record["mod_key"] != review["mod_key"]:
                raise ValueError(f"Conflicting source mod_key: {path} / {record['mechanic_id']}")
            identity = (record["mod_key"], record["mechanic_id"])
            if identity in identities:
                raise ValueError(f"Duplicate source mechanic identity: {identity}")
            identities.add(identity)
            records.append(record)
    return {
        "schema_version": 1,
        "source_ref": source_ref,
        "source_commit": commit,
        "source_reviews": list(REVIEW_FILES),
        "text_excerpt_limit": EXCERPT_LIMIT,
        "mechanics": sorted(records, key=lambda record: (record["mod_key"], record["mechanic_id"])),
    }


def serialize_manifest(manifest):
    """Standard JSON, with one compact mechanic per line for bounded diffs."""
    metadata = {key: value for key, value in manifest.items() if key != "mechanics"}
    header = json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)[:-2]
    rows = [json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for record in manifest["mechanics"]]
    body = ",\n".join("    " + row for row in rows)
    return (header + ',\n  "mechanics": [\n' + body + '\n  ]\n}\n').encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=SOURCE_REF, help="Source Git ref or pinned review commit")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        commit, reviews = read_reviews(REPO_ROOT, args.ref)
        manifest = compile_manifest(reviews, commit, args.ref)
        payload = serialize_manifest(manifest)
    except (ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {len(manifest['mechanics'])} mechanics from {len(reviews)} completed reviews to {args.output}")


if __name__ == "__main__":
    main()

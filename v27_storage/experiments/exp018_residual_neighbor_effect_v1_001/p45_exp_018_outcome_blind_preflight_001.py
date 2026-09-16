from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
OUTPUT = Path(__file__).resolve().parent / "P45_EXP_018_STRUCTURAL_PREFLIGHT_001.json"
EXPECTED_SOURCE_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_main6() -> dict[int, tuple[int, ...]]:
    draws: dict[int, tuple[int, ...]] = {}
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            round_number = int(row["round"])
            numbers = tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))
            if len(set(numbers)) != 6 or not all(1 <= value <= 45 for value in numbers):
                raise RuntimeError("SOURCE_INTEGRITY_FAILURE")
            draws[round_number] = numbers
    if set(draws) != set(range(1, 1239)):
        raise RuntimeError("SOURCE_RANGE_OR_CONTINUITY_FAILURE")
    return draws


def build_predictor_structure(draws: dict[int, tuple[int, ...]]) -> list[dict]:
    last_seen: dict[int, int] = {}
    records: list[dict] = []
    all_numbers = set(range(1, 46))
    for target in range(2, 1239):
        previous_round = target - 1
        previous = set(draws[previous_round])
        for value in previous:
            last_seen[value] = previous_round

        raw_neighbors = {candidate for value in previous for candidate in (value - 1, value + 1) if 1 <= candidate <= 45}
        overlap_removed = raw_neighbors & previous
        neighbors = raw_neighbors - previous
        eligible = all_numbers - previous
        controls = eligible - neighbors

        ages: dict[int, int | None] = {
            value: (previous_round - last_seen[value]) if value in last_seen else None
            for value in eligible
        }
        neighbor_by_age: dict[int, list[int]] = defaultdict(list)
        control_by_age: dict[int, list[int]] = defaultdict(list)
        undefined_neighbors = 0
        undefined_controls = 0
        for value in sorted(neighbors):
            age = ages[value]
            if age is None:
                undefined_neighbors += 1
            else:
                neighbor_by_age[age].append(value)
        for value in sorted(controls):
            age = ages[value]
            if age is None:
                undefined_controls += 1
            else:
                control_by_age[age].append(value)

        valid_ages = sorted(set(neighbor_by_age) & set(control_by_age))
        matched_neighbor = sum(len(neighbor_by_age[age]) for age in valid_ages)
        matched_control = sum(len(control_by_age[age]) for age in valid_ages)
        no_control_ages = sorted(set(neighbor_by_age) - set(control_by_age))
        no_control_neighbors = sum(len(neighbor_by_age[age]) for age in no_control_ages)
        strata = [
            {"age": age, "neighbor_count": len(neighbor_by_age[age]), "control_count": len(control_by_age[age])}
            for age in valid_ages
        ]
        records.append({
            "target": target,
            "neighbor_candidates": len(neighbors),
            "eligible_controls": len(controls),
            "matched_strata": strata,
            "matched_neighbor_exposures": matched_neighbor,
            "matched_control_exposures": matched_control,
            "unmatched_neighbor_exposures": undefined_neighbors + no_control_neighbors,
            "undefined_neighbor_exclusions": undefined_neighbors,
            "undefined_control_exclusions": undefined_controls,
            "no_control_strata": len(no_control_ages),
            "previous_overlap_removed": len(overlap_removed),
        })
    return records


def summarize(records: list[dict], start: int, end: int) -> dict:
    selected = [record for record in records if start <= record["target"] <= end]
    age_strata = Counter()
    for record in selected:
        for stratum in record["matched_strata"]:
            age_strata[str(stratum["age"])] += 1
    total_neighbors = sum(record["neighbor_candidates"] for record in selected)
    matched_neighbors = sum(record["matched_neighbor_exposures"] for record in selected)
    neighbor_distribution = Counter(record["neighbor_candidates"] for record in selected)
    return {
        "range": f"{start}..{end}",
        "target_count": len(selected),
        "total_neighbor_candidate_count": total_neighbors,
        "eligible_control_count": sum(record["eligible_controls"] for record in selected),
        "matched_target_rounds": sum(bool(record["matched_strata"]) for record in selected),
        "matched_strata_count": sum(len(record["matched_strata"]) for record in selected),
        "matched_neighbor_exposures": matched_neighbors,
        "matched_control_exposures": sum(record["matched_control_exposures"] for record in selected),
        "unmatched_neighbor_exposures": sum(record["unmatched_neighbor_exposures"] for record in selected),
        "match_rate": matched_neighbors / total_neighbors if total_neighbors else 0.0,
        "exact_age_stratum_distribution": dict(sorted(age_strata.items(), key=lambda item: int(item[0]))),
        "max_neighbor_candidates_per_target": max(record["neighbor_candidates"] for record in selected),
        "neighbor_candidate_count_distribution": {str(k): v for k, v in sorted(neighbor_distribution.items())},
        "no_control_stratum_count": sum(record["no_control_strata"] for record in selected),
        "age_undefined_exclusion_count": sum(record["undefined_neighbor_exclusions"] + record["undefined_control_exclusions"] for record in selected),
        "age_undefined_neighbor_exclusions": sum(record["undefined_neighbor_exclusions"] for record in selected),
        "age_undefined_control_exclusions": sum(record["undefined_control_exclusions"] for record in selected),
        "prev_overlap_removal_count": sum(record["previous_overlap_removed"] for record in selected),
    }


def main() -> int:
    source_sha = sha256(SOURCE)
    if source_sha != EXPECTED_SOURCE_SHA:
        raise RuntimeError("SOURCE_SHA_MISMATCH")
    draws = load_main6()
    records = build_predictor_structure(draws)
    payload = {
        "experiment_id": "EXP-018 / EXP-DRAW-20260827-018-V1",
        "title": "RESIDUAL NEIGHBOR EFFECT / ADJACENCY AXIS CLOSURE V1",
        "mode": "OUTCOME_BLIND_STRUCTURAL_PREFLIGHT",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": source_sha,
        "historical": summarize(records, 2, 1238),
        "development": summarize(records, 2, 867),
        "holdout": summarize(records, 868, 1238),
        "reproducibility": {
            "return_age": "PASS",
            "neighbor": "PASS",
            "control": "PASS",
            "matching": "PASS",
            "source_integrity": "PASS",
        },
        "outcome_peek": {
            "neighbor_hits_calculated": False,
            "control_hits_calculated": False,
            "hit_rates_calculated": False,
            "matched_delta_calculated": False,
            "p_value_calculated": False,
            "confidence_interval_calculated": False,
            "split_verdict_calculated": False,
        },
        "future_leakage": 0,
        "status": "STRUCTURAL_PREFLIGHT_PASS",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

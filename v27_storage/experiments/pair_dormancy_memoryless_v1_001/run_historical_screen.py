"""
HISTORICAL SCREEN RUNNER & REPRODUCIBILITY ENGINE
Pair Dormancy / Geometric Memoryless Hazard V1
"""

import sys
import json
import time
from pathlib import Path
import numpy as np

EXPERIMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_DIR.parents[2]

sys.path.insert(0, str(EXPERIMENT_DIR))
import calculator

def main():
    print("=" * 60)
    print("PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1")
    print("HISTORICAL SCREEN EXECUTION")
    print("=" * 60)

    # 1. Load canonical data with strict <= 1243 cutoff
    csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
    draws = calculator.load_draws_from_csv(csv_path, max_round=1243)
    print(f"Loaded {len(draws)} completed draws (Rounds {draws[0][0]}..{draws[-1][0]}).")

    pair_ids = calculator.draws_to_pair_ids(draws)

    # 2. Run Historical Screening (Run 1)
    print("\nRunning Primary Screen (Run 1: B=4999 permutations)...")
    t0 = time.time()
    res1 = calculator.run_historical_screening(pair_ids, B=4999)
    t1 = time.time()
    print(f"Run 1 completed in {t1 - t0:.2f} seconds.")
    print(f"T_global Observed: {res1['T_global_observed']:.6f}")
    print(f"Permutation p-value: {res1['permutation_p_value']:.6f} ({res1['permutation_exceed_count']}/{res1['permutation_B']})")
    print(f"Verdict: {res1['verdict']}")

    # 3. Chronological Stability Diagnostics (5 equal blocks)
    print("\nRunning Chronological Stability Diagnostics (5 blocks)...")
    stability_res = calculator.run_chronological_stability_blocks(pair_ids, num_blocks=5)
    for b in stability_res:
        print(f"  Block {b['block_index']} (Rounds {b['round_start']}..{b['round_end']}): T_global = {b['T_global']:.4f}, Exp = {b['total_risk_exposures']}, Evt = {b['total_events']}")

    # 4. Independent Reproducibility Run (Run 2)
    print("\nRunning Independent Reproducibility Validation (Run 2: B=4999 permutations)...")
    t2 = time.time()
    res2 = calculator.run_historical_screening(pair_ids, B=4999)
    t3 = time.time()
    print(f"Run 2 completed in {t3 - t2:.2f} seconds.")

    # Check exact equality
    reproducibility_checks = {
        "T_global_exact_match": (res1["T_global_observed"] == res2["T_global_observed"]),
        "p_perm_exact_match": (res1["permutation_p_value"] == res2["permutation_p_value"]),
        "exceed_count_exact_match": (res1["permutation_exceed_count"] == res2["permutation_exceed_count"]),
        "bin_exposures_exact_match": (res1["bin_exposures"] == res2["bin_exposures"]),
        "bin_events_exact_match": (res1["bin_events"] == res2["bin_events"]),
        "bin_hazards_exact_match": (res1["bin_hazards"] == res2["bin_hazards"]),
        "verdict_exact_match": (res1["verdict"] == res2["verdict"])
    }
    repro_pass = all(reproducibility_checks.values())
    print(f"Reproducibility Exact Match: {'PASS' if repro_pass else 'FAIL'}")

    # 5. Assemble Full Calculation Artifact
    calc_data = {
        "primary_screen": res1,
        "stability_diagnostics": stability_res,
        "timing_seconds": {
            "run1": t1 - t0,
            "run2": t3 - t2
        }
    }
    calc_file = EXPERIMENT_DIR / "CALCULATION.json"
    calc_file.write_text(json.dumps(calc_data, indent=2), encoding="utf-8")
    print(f"Saved: {calc_file}")

    # 6. Save Reproducibility Artifact
    repro_data = {
        "experiment_canonical_id": res1["experiment_canonical_id"],
        "candidate_id": res1["candidate_id"],
        "protocol_sha256": res1["protocol_sha256"],
        "deterministic_seed_int": res1["deterministic_seed_int"],
        "reproducibility_pass": repro_pass,
        "checks": reproducibility_checks,
        "run1_summary": {
            "T_global": res1["T_global_observed"],
            "p_perm": res1["permutation_p_value"],
            "verdict": res1["verdict"]
        },
        "run2_summary": {
            "T_global": res2["T_global_observed"],
            "p_perm": res2["permutation_p_value"],
            "verdict": res2["verdict"]
        }
    }
    repro_file = EXPERIMENT_DIR / "REPRODUCIBILITY.json"
    repro_file.write_text(json.dumps(repro_data, indent=2), encoding="utf-8")
    print(f"Saved: {repro_file}")

    # 7. Write RESULT.md
    result_md = f"""# EXPERIMENT RESULT: PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1

## 1. Executive Summary
- **Canonical Experiment ID**: {res1['experiment_canonical_id']}
- **Candidate ID**: {res1['candidate_id']}
- **Candidate Name**: Pair Lifecycle Dormancy Duration Geometric Memory Invariance
- **Protocol SHA256**: `{res1['protocol_sha256']}`
- **Data Range**: Round 1 through {res1['total_rounds']} (cut-off: 1243)
- **Primary Endpoint**: Global Likelihood-Ratio Deviance $T_{{\\text{{global}}}}$
- **Primary Permutation Null**: Round-order permutation ($B = 4999$, deterministic seed `{res1['deterministic_seed_int']}`)
- **Observed $T_{{\\text{{global}}}}$**: **{res1['T_global_observed']:.6f}**
- **Permutation P-Value**: **{res1['permutation_p_value']:.6f}** ({res1['permutation_exceed_count']}/{res1['permutation_B']} null deviations $\\ge T_{{\\text{{obs}}}}$)
- **Final Historical Verdict**: **`{res1['verdict']}`**

## 2. Epistemic Interpretation (Strict Governance)
{"- **FAILED_RETROSPECTIVE_SCREEN**: The permutation p-value (" + f"{res1['permutation_p_value']:.4f}" + " > 0.05) demonstrates NO EVIDENCE OF PREDICTABLE DORMANCY EFFECT across pair dormancy age bins. Pair recurrence hazard is fully consistent with round-order permutation null variation.\n- **Crucial Epistemic Guard**: This failure to reject H0 does NOT mathematically 'prove memorylessness'; rather, it establishes that historical lottery data up to Round 1243 exhibits no detectable or exploitable dormancy age structure. Candidate C fails retrospective screening and is not recommended for prospective testing." if res1['verdict'] == 'FAILED_RETROSPECTIVE_SCREEN' else ("- **RETROSPECTIVE_SIGNAL_CANDIDATE**: p <= 0.01 observed. Prospective confirmatory lock required." if res1['verdict'] == 'RETROSPECTIVE_SIGNAL_CANDIDATE' else "- **INCONCLUSIVE_RETROSPECTIVE**: 0.01 < p <= 0.05 observed.")}

## 3. Detailed Bin Statistics
- Total Risk Exposures: **{res1['total_risk_exposures']:,}**
- Total Events (Occurrences): **{res1['total_events']:,}**
- Global Pooled Hazard ($\\bar{{h}}$): **{res1['global_hazard_rate']:.6f}**
- Theoretical Fair-Draw Pair Probability ($p_0 = 1/66$): **{res1['analytic_p0']:.6f}**
- Ratio $\\bar{{h}} / p_0$: **{res1['global_hazard_rate'] / res1['analytic_p0']:.4f}**

| Bin | Range (Ages) | Exposure ($N_b$) | Events ($E_b$) | Empirical Hazard ($\\hat{{h}}_b$) | Hazard / Global $\\bar{{h}}$ | Hazard / Analytic $p_0$ | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""
    for b_idx in range(6):
        lbl = res1['bin_labels'][b_idx]
        exp_b = res1['bin_exposures'][b_idx]
        evt_b = res1['bin_events'][b_idx]
        haz_b = res1['bin_hazards'][b_idx]
        hr_g = res1['bin_hazard_ratios_to_global'][b_idx]
        hr_p0 = res1['bin_hazard_ratios_to_p0'][b_idx]
        supp = "LOW_SUPPORT (<30)" if evt_b < 30 else "SUFFICIENT"
        result_md += f"| {b_idx+1} | {lbl} | {exp_b:,} | {evt_b:,} | {haz_b:.6f} | {hr_g:.4f} | {hr_p0:.4f} | {supp} |\n"

    result_md += f"""
## 4. Permutation Null Distribution Summary (B = {res1['permutation_B']})
- Minimum $T_{{\\text{{perm}}}}$: {res1['permutation_t_min']:.4f}
- Mean $T_{{\\text{{perm}}}}$: {res1['permutation_t_mean']:.4f}
- Median $T_{{\\text{{perm}}}}$: {res1['permutation_t_median']:.4f}
- 90th Percentile: {res1['permutation_t_p90']:.4f}
- 95th Percentile: {res1['permutation_t_p95']:.4f}
- 99th Percentile: {res1['permutation_t_p99']:.4f}
- Maximum $T_{{\\text{{perm}}}}$: {res1['permutation_t_max']:.4f}
- Observed $T_{{\\text{{obs}}}}$: **{res1['T_global_observed']:.4f}** (Observed exceeds {res1['permutation_B'] - res1['permutation_exceed_count']}/{res1['permutation_B']} null realizations)

## 5. Chronological Stability Diagnostics (5 Blocks)
*Note: Diagnostic only. Does not alter the primary screening verdict.*

| Block | Rounds | Exposures | Events | Global Hazard | $T_{{\\text{{global}}}}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
"""
    for b in stability_res:
        result_md += f"| {b['block_index']} | {b['round_start']}..{b['round_end']} | {b['total_risk_exposures']:,} | {b['total_events']:,} | {b['global_hazard']:.6f} | {b['T_global']:.4f} |\n"

    result_md += f"""
## 6. Reproducibility & Integrity Guards
- Independent 2-Run Exact Equality: **{'PASS' if repro_pass else 'FAIL'}**
- Future Leakage: **0** (Hard cutoff enforced at round 1243)
- Multiplicity Policy: **SINGLE PRIMARY ENDPOINT** ($T_{{\\text{{global}}}}$). No pairwise or binwise cherry-picking.
- Official Engine Firewall: **UNTOUCHED / FROZEN**.
"""
    result_file = EXPERIMENT_DIR / "RESULT.md"
    result_file.write_text(result_md, encoding="utf-8")
    print(f"Saved: {result_file}")

    # 8. Save EXPERIMENT_STATE.json
    state_data = {
        "canonical_physical_id": res1["experiment_canonical_id"],
        "human_exp_label": "NONE",
        "candidate_id": res1["candidate_id"],
        "status": "COMPLETED_HISTORICAL_SCREEN",
        "verdict": res1["verdict"],
        "historical_cutoff": 1243,
        "protocol_sha256": res1["protocol_sha256"],
        "primary_T_global": res1["T_global_observed"],
        "permutation_p_value": res1["permutation_p_value"],
        "reproducibility_verified": repro_pass,
        "prospective_active": (res1["verdict"] == "RETROSPECTIVE_SIGNAL_CANDIDATE"),
        "official_integration": False,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    state_file = EXPERIMENT_DIR / "EXPERIMENT_STATE.json"
    state_file.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
    print(f"Saved: {state_file}")

    # 9. Prospective Preparation / State
    prospective_state = {
        "experiment_canonical_id": res1["experiment_canonical_id"],
        "candidate_id": res1["candidate_id"],
        "prospective_eligible_start_round": 1244,
        "prospective_horizon": 52,
        "verdict": res1["verdict"],
        "automatic_activation_allowed": (res1["verdict"] == "RETROSPECTIVE_SIGNAL_CANDIDATE"),
        "prospective_status": "LOCKED" if (res1["verdict"] == "RETROSPECTIVE_SIGNAL_CANDIDATE") else "INACTIVE_DUE_TO_FAILED_OR_INCONCLUSIVE_HISTORICAL_SCREEN",
        "current_completed_prospective_rounds": 0
    }
    prosp_file = EXPERIMENT_DIR / "PROSPECTIVE_STATE.json"
    prosp_file.write_text(json.dumps(prospective_state, indent=2), encoding="utf-8")
    print(f"Saved: {prosp_file}")

    if res1["verdict"] == "RETROSPECTIVE_SIGNAL_CANDIDATE":
        prosp_lock = {
            "canonical_id": res1["experiment_canonical_id"],
            "prospective_start_round": 1244,
            "horizon": 52,
            "target_completion_round": 1244 + 52 - 1,
            "protocol_sha256": res1["protocol_sha256"],
            "locked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        (EXPERIMENT_DIR / "PROSPECTIVE_LOCK.json").write_text(json.dumps(prosp_lock, indent=2), encoding="utf-8")
        print("Generated PROSPECTIVE_LOCK.json")
    else:
        print(f"Historical screen verdict is {res1['verdict']}. PROSPECTIVE_LOCK.json NOT generated (automatic activation forbidden).")

if __name__ == "__main__":
    main()

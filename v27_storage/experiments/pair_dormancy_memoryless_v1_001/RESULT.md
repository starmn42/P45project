# EXPERIMENT RESULT: PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1

## 1. Executive Summary
- **Canonical Experiment ID**: EXP-DRAW-20261001-001-V1
- **Candidate ID**: IDEA-1243-CROS-003
- **Candidate Name**: Pair Lifecycle Dormancy Duration Geometric Memory Invariance
- **Protocol SHA256**: `7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a`
- **Data Range**: Round 1 through 1243 (cut-off: 1243)
- **Primary Endpoint**: Global Likelihood-Ratio Deviance $T_{\text{global}}$
- **Primary Permutation Null**: Round-order permutation ($B = 4999$, deterministic seed `2359884131`)
- **Observed $T_{\text{global}}$**: **4.627019**
- **Permutation P-Value**: **0.622400** (3111/4999 null deviations $\ge T_{\text{obs}}$)
- **Final Historical Verdict**: **`FAILED_RETROSPECTIVE_SCREEN`**

## 2. Epistemic Interpretation (Strict Governance)
- **FAILED_RETROSPECTIVE_SCREEN**: The permutation p-value (0.6224 > 0.05) demonstrates NO EVIDENCE OF PREDICTABLE DORMANCY EFFECT across pair dormancy age bins. Pair recurrence hazard is fully consistent with round-order permutation null variation.
- **Crucial Epistemic Guard**: This failure to reject H0 does NOT mathematically 'prove memorylessness'; rather, it establishes that historical lottery data up to Round 1243 exhibits no detectable or exploitable dormancy age structure. Candidate C fails retrospective screening and is not recommended for prospective testing.

## 3. Detailed Bin Statistics
- Total Risk Exposures: **1,162,896**
- Total Events (Occurrences): **17,655**
- Global Pooled Hazard ($\bar{h}$): **0.015182**
- Theoretical Fair-Draw Pair Probability ($p_0 = 1/66$): **0.015152**
- Ratio $\bar{h} / p_0$: **1.0020**

| Bin | Range (Ages) | Exposure ($N_b$) | Events ($E_b$) | Empirical Hazard ($\hat{h}_b$) | Hazard / Global $\bar{h}$ | Hazard / Analytic $p_0$ | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | B1 [1..12] | 204,814 | 3,076 | 0.015019 | 0.9892 | 0.9912 | SUFFICIENT |
| 2 | B2 [13..27] | 206,460 | 3,211 | 0.015553 | 1.0244 | 1.0265 | SUFFICIENT |
| 3 | B3 [28..46] | 198,353 | 2,938 | 0.014812 | 0.9756 | 0.9776 | SUFFICIENT |
| 4 | B4 [47..72] | 190,867 | 2,884 | 0.015110 | 0.9953 | 0.9973 | SUFFICIENT |
| 5 | B5 [73..118] | 191,397 | 2,942 | 0.015371 | 1.0125 | 1.0145 | SUFFICIENT |
| 6 | B6 [119+] | 171,005 | 2,604 | 0.015228 | 1.0030 | 1.0050 | SUFFICIENT |

## 4. Permutation Null Distribution Summary (B = 4999)
- Minimum $T_{\text{perm}}$: 0.0708
- Mean $T_{\text{perm}}$: 6.6147
- Median $T_{\text{perm}}$: 5.7324
- 90th Percentile: 12.3955
- 95th Percentile: 14.5910
- 99th Percentile: 20.2109
- Maximum $T_{\text{perm}}$: 32.2691
- Observed $T_{\text{obs}}$: **4.6270** (Observed exceeds 1888/4999 null realizations)

## 5. Chronological Stability Diagnostics (5 Blocks)
*Note: Diagnostic only. Does not alter the primary screening verdict.*

| Block | Rounds | Exposures | Events | Global Hazard | $T_{\text{global}}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 1..248 | 180,713 | 2,759 | 0.015267 | 10.9514 |
| 2 | 249..496 | 181,687 | 2,759 | 0.015185 | 3.0498 |
| 3 | 497..744 | 182,577 | 2,745 | 0.015035 | 6.2653 |
| 4 | 745..992 | 179,671 | 2,750 | 0.015306 | 2.2116 |
| 5 | 993..1243 | 184,804 | 2,790 | 0.015097 | 4.4845 |

## 6. Reproducibility & Integrity Guards
- Independent 2-Run Exact Equality: **PASS**
- Future Leakage: **0** (Hard cutoff enforced at round 1243)
- Multiplicity Policy: **SINGLE PRIMARY ENDPOINT** ($T_{\text{global}}$). No pairwise or binwise cherry-picking.
- Official Engine Firewall: **UNTOUCHED / FROZEN**.

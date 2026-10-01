# EXPERIMENT PROTOCOL: PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1

## 1. Candidate Identification & Heritage
- **Candidate ID**: IDEA-1243-CROS-003
- **Candidate Name**: Pair Lifecycle Dormancy Duration Geometric Memory Invariance
- **Candidate Birth Round**: 1243
- **Discovery Data End Round**: 1243
- **Identity Fingerprint**: 2f7f3e183e5e837723232cbdf5e7ab292fbf2e3e04ce3173dc8bd79db0fc09f5
- **Canonical Experiment ID**: EXP-DRAW-20261001-001-V1
- **Human Experiment Label**: NONE (UNASSIGNED)
- **Experiment Family**: PAIR DORMANCY MEMORYLESS HAZARD LAB
- **Experiment Title**: PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1

## 2. Hypotheses
### 2.1 Original Candidate Hypotheses (Preserved Exact)
- **Candidate Hypothesis**: `Pair lifecycle dormancy durations (gap rounds between occurrences) follow the memoryless geometric distribution, confirming complete temporal independence of ball pairings.`
- **Candidate Opposite Hypothesis**: `Pair lifecycle dormancy exhibits non-geometric hazard aging or structural clustering.`

### 2.2 Operational Statistical Hypotheses
- **H0 (Null Hypothesis)**: If the completed draw process is temporal-memory-free, the observed variations in next-round pair occurrence hazard across dormancy age bins are within the distribution expected under round-order permutations.
- **H1 (Alternative Hypothesis)**: The next-round pair occurrence hazard structure across dormancy age bins differs significantly from the round-order permutation null distribution.

*Epistemic Note*: Failure to reject H0 does NOT prove memorylessness. It demonstrates: "NO EVIDENCE OF PREDICTABLE DORMANCY EFFECT". Rejection of H0 (p <= 0.01) does NOT prove actionable predictability; it indicates: "RETROSPECTIVE_SIGNAL_CANDIDATE / PROSPECTIVE CONFIRMATION REQUIRED".

## 3. Mathematical Universe & Definitions
- **Ball Universe**: MAIN numbers 1..45. BONUS numbers are completely excluded from V1 primary and secondary analyses.
- **Unordered Pair Space**: Total pairs = C(45, 2) = 990.
- **Pairs Per Draw**: In each draw of 6 MAIN numbers, exactly C(6, 2) = 15 unordered pairs appear.
- **Analytic Fair-Draw Probability**:
  $$p_0 = \frac{\binom{43}{4}}{\binom{45}{6}} = \frac{6 \times 5}{45 \times 44} = \frac{30}{1980} = \frac{1}{66} \approx 0.0151515...$$
- **Dormancy Age**:
  For pair $i$ evaluated at target round $t$, let $s < t$ be the round of its most recent prior occurrence.
  $$\text{dormancy\_age}(i, t) = t - s$$
  - If pair $i$ appeared in round $t-1$, $\text{dormancy\_age}(i, t) = 1$.
  - The outcome of round $t$ is strictly forbidden from entering the calculation of $\text{dormancy\_age}(i, t)$.
  - After round $t$ completes, if pair $i$ appeared, its age resets to 1 at round $t+1$; otherwise its age increments to $\text{dormancy\_age}(i, t) + 1$.
- **Left-Censoring Exclusion**:
  Before a pair makes its first historical appearance in the completed draw record, its dormancy duration is left-censored (unknown start). All such pair-round pairs are marked `LEFT_CENSORED` and excluded from the risk exposure set. Only rounds strictly following the first appearance of pair $i$ enter the risk exposure set.

## 4. Fixed Dormancy Bins (Pre-experimental Lock)
Bins are derived strictly from the analytic geometric distribution quantiles with $p_0 = 1/66$:
$$F(x) = 1 - (1 - p_0)^x = 1 - \left(\frac{65}{66}\right)^x, \quad x_q = \frac{\ln(1 - q)}{\ln(65/66)}$$
For $q \in \{1/6, 2/6, 3/6, 4/6, 5/6\}$:
- $q = 1/6 \implies x \approx 11.94 \implies B_1 = [1, 12]$
- $q = 2/6 \implies x \approx 26.56 \implies B_2 = [13, 27]$
- $q = 3/6 \implies x \approx 45.40 \implies B_3 = [28, 46]$
- $q = 4/6 \implies x \approx 71.96 \implies B_4 = [47, 72]$
- $q = 5/6 \implies x \approx 117.36 \implies B_5 = [73, 118]$
- Tail $\implies B_6 = [119, \infty)$

These bin boundaries are locked before inspection of lottery data. Post-hoc bin tuning is strictly forbidden.

## 5. Primary Test Statistic & Inference
- **Bin Risk Exposures & Events**:
  For bin $b \in \{1..6\}$:
  - $N_b$: Total pair-round evaluations where pair dormancy age fell in bin $b$.
  - $E_b$: Total occurrences (events) among those evaluations.
  - $\hat{h}_b = E_b / N_b$: Empirical hazard rate in bin $b$.
  - $\bar{h} = \sum_{b=1}^6 E_b / \sum_{b=1}^6 N_b$: Pooled global hazard rate.
- **Primary Test Statistic**: Global Likelihood-Ratio Deviance
  $$T_{\text{global}} = 2 \sum_{b=1}^6 \left[ E_b \ln\left(\frac{\hat{h}_b}{\bar{h}}\right) + (N_b - E_b) \ln\left(\frac{1 - \hat{h}_b}{1 - \bar{h}}\right) \right]$$
  (Standard convention: $0 \ln(0) = 0$).
- **Primary Endpoint Multiplicity**: Exactly ONE primary test statistic ($T_{\text{global}}$).
  - No 990 individual pair p-values.
  - No bin-specific primary tests.
- **Primary Null Distribution**: Round-Order Permutation Null.
  - Permutes the chronological order of the completed MAIN6 draws (1..1243).
  - Preserves: draw compositions, 15 pairs per draw, marginal number frequencies, pair total counts.
  - Destroys: temporal ordering, clustering, dormancy sequences.
- **Permutation Count**: $B = 4999$.
- **Deterministic PRNG Seed**:
  Derived via SHA-256: `int(sha256(protocol_sha + canonical_id + "PAIR_DORMANCY_MEMORYLESS_V1")[:8], 16)`.
- **Permutation P-Value**:
  $$p_{\text{perm}} = \frac{1 + \sum_{k=1}^B \mathbb{I}(T_{\text{perm}, k} \ge T_{\text{obs}})}{B + 1}$$

## 6. Decision Rules & Evidence Status
- **Historical Retrospective Screen**:
  - $p_{\text{perm}} \le 0.01 \implies \text{RETROSPECTIVE\_SIGNAL\_CANDIDATE}$ (Eligible for prospective lock; NOT supported).
  - $0.01 < p_{\text{perm}} \le 0.05 \implies \text{INCONCLUSIVE\_RETROSPECTIVE}$ (No automatic prospective lock).
  - $p_{\text{perm}} > 0.05 \implies \text{FAILED\_RETROSPECTIVE\_SCREEN}$ (Candidate retired/failed; no rescue).
- **Prohibition on Confirmatory Claim**:
  Because Candidate C was formulated after observing data up to round 1243, retrospective testing cannot be claimed as a confirmatory holdout.
- **Prospective Horizon & Criteria**:
  - Prospective evaluation horizon: 52 completed future rounds.
  - Early stopping or intermediate p-value fishing: FORBIDDEN.
  - Prospective success: $p_{\text{perm}} \le 0.01 \implies \text{PROSPECTIVE\_TEMPORAL\_EFFECT\_SUPPORTED}$.
  - Prospective inconclusive: $0.01 < p_{\text{perm}} \le 0.05 \implies \text{PROSPECTIVE\_INCONCLUSIVE}$.
  - Prospective failure: $p_{\text{perm}} > 0.05 \implies \text{PROSPECTIVE\_NOT\_SUPPORTED}$.

## 7. Data Cutoff & Future Leakage Firewall
- Historical data cutoff: $t \le 1243$ (`discovery_data_end_round`).
- Draws with $t > 1243$ are strictly excluded from historical calculations.
- Prospective start round: First round whose outcome is unknown at protocol lock (Round 1244).
- Official Engine Firewall:
  - Official DB, Gates, Thresholds, Signatures, 1244 Sealed Predraw, and Recommended Picks are 100% FROZEN.
  - Zero official promotion without a subsequent separate actionability experiment.

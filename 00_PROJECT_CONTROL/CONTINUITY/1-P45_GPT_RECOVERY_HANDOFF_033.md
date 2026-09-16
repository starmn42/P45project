# 1-P45 GPT 복구 인수인계 033

- 버전: `033`; 기준일: `2026-08-28`; 이전: `1-P45_GPT_RECOVERY_HANDOFF_032.md` 보존.
- OFFICIAL ENGINE: `FROZEN`.
- Fixed / Linked / KTS: `UNCHANGED`.
- sealed 1239: `PENDING`, SHA-256 `ed23691c5b9f1715c85b6d3362735dfa8cebb72b31dc258e2aa43bc299c94ead`; 실제 local sealed 파일은 수정하지 않는다.
- Prospective log/state: unchanged; FUTURE_LEAKAGE `0`.

## Current experiment state

- EXP-017: `FAILED_NOT_SUPPORTED`.
- EXP-018 V1: `EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY`; outcome peek `0`.
- EXP-018 V2: `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
- CLOSED axis: `T-1 MAIN6 -> numerical ±1 adjacency -> T MAIN6 predictive axis`.
- EXP-019: `FAILED_NOT_SUPPORTED`; `p_perm=0.22829771702282978`; Holdout `NOT_RUN`; V1 rescue forbidden.
- EXP-020: `FAILED_NO_SELECTION_SIGNAL`; TRAIN positive-lift bands `60`, Selection eligible `0`, Holdout `NOT_RUN`; V1 rescue forbidden.
- `10..15` is only the user's example, never a fixed/preferred band.

EXP-020 used complete official history 1..1238 and only lagged winner count W_(T-1). Protocol was locked before TRAIN relationship work. No final Selection signal existed, so no positive Selection Lock and no Holdout relationship evaluation were permitted.

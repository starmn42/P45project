# P45 전체 연구 마스터 인덱스 002

## 문서 지위와 복구 순위

- 기준일: `2026-08-28`
- 이 문서는 전체 연구 존재 여부와 집계의 기준이다.
- 프로젝트 복구 우선순위는 `latest Recovery/Handoff` → `latest Core Guide` → 이 Master 및 원본 Result다.
- 빠른 안내문인 `P45_NEW_CHAT_START_HERE`는 Recovery보다 상위 근거가 아니다.
- Official Engine은 `FROZEN`; 사용자 명시 승인 전 변경하지 않는다.
- `3/3=PRIMARY`, `exact 2/3=SUPPORT`; 혼합판정 금지.

## 최종 counting policy — 53과 68

`COUNT_DISCREPANCY_FULLY_RECONCILED`

- authoritative Registry: `00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md`
- formal registry rows: `68` canonical physical/version rows. 행 첫 필드가 `EXP-(DRAW|CROWD|PRIZE|CROSS)-YYYYMMDD-NNN-Vn`인 행을 1건으로 센다.
- domain split: `DRAW 53 + CROWD 9 + PRIZE 6 = 68`.
- `P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`의 `53`은 `EXP-DRAW-*` 행만 추출한 DRAW-domain snapshot이다. 전체 formal Registry snapshot이 아니다.
- difference 15: CROWD 9행 + PRIZE 6행. 중복·삭제·추정 보정이 아니다.
- versions: `V1 65`, `V2 3`; version row는 각각 physical row로 센다.
- latest numbered DRAW experiment: `EXP-020`. 마지막 EXP 번호와 Registry row 수는 서로 다른 필드다.
- 과거 count audit의 `58`은 2026-08-23 시점 값이며 이후 canonical append로 68이 됐다. Registry 말미의 EXP-020 기록이 현재 68을 명시한다.

## 최종 집계

|구분|수|정의|
|---|---:|---|
|공식 내부 연구|12|Official 구조/운영 연구 축|
|정식 Registry physical/version rows|68|DRAW 53 + CROWD 9 + PRIZE 6|
|실제 실행 완료 정식 rows|27|결과·settlement·공식 change-control 완료 상태가 있는 행|
|등록/설계/대기/차단 rows|41|REGISTERED 36, DESIGNED 1, READY_FOR_TEST 1, source-semantics blocked 1, prospective waiting 2|
|프로토콜/실행 차단|2|PRIZE V1 source-semantics 1 + EXP-018 V1 bootstrap ambiguity 1|
|축폐쇄|1|EXP-018 V2 adjacency axis|
|EXP 외 실제 연구|27|정식 canonical Registry ID 없이 계산·검증된 연구 축|
|미실행 검토 아이디어|2|DRAW-ORDER, REHEARSAL|

정식 실행 완료 `27`에는 일반 신호연구뿐 아니라 Registry에 정식 행으로 기록된 공식 repair change-control 1건도 포함한다. 이를 예측 신호 성공으로 해석하지 않는다.

## A. 공식 엔진 내부 연구 — 12개

|구조|실제 의미와 상태|근거|
|---|---|---|
|UNIT_3|3단위 점유·전멸·복귀. 1239 rerun NORMAL 69.1188.|v2.7 설계, current-1239 rerun|
|UNIT_5|5단위 점유·전멸·복귀. 과거 SEVERE 99.1909와 contiguous 재구축 후 NORMAL 57.4778을 구분.|number-member trace, rerun|
|UNIT_9|9단위 전멸구간·복귀깊이 0/1/2. 1239 rerun NORMAL 62.4091.|v2.5/v2.7, rerun|
|UNIT_10|10단위 전멸구간과 41..45 크기 보정. 1239 rerun NORMAL 65.4002.|v2.7, rerun|
|END_DIGIT|끝수 점유·전멸·복귀. 1239 SEVERE 100.0.|1239 root-cause trace|
|NUMBER|개별 번호 구조·멤버십 관문. 1239 selected 0.|1239 predraw/rerun|
|TRIO|핵심 조합 단위. `3/3 PRIMARY`, `exact2/3 SUPPORT`.|Core Guide|
|PAIR|lifecycle/signature/timing shadow repair와 승인 change-control.|repair audits|
|CORE|NUMBER→TRIO→PAIR→CORE 보호 판정 계층.|Core Guide/manifests|
|Fixed Orbit|고정 KTS 3×3 TRIO; 역사 exact3 5/1237.|TRIO ORBIT result|
|Linked Orbit|직전 MAIN6+BONUS 연동 3×3 TRIO; 역사 exact3 7/1237, 우월성 미지지.|TRIO ORBIT/divergence|
|KTS45|330 TRIO 고정 schedule; 결과 후 재생성 금지.|locked schedule/protocol|

UNIT_5·UNIT_9·UNIT_10 전멸구간은 설계 원문에 존재하며 누락하지 않는다. 현재 rerun과 과거 snapshot을 혼동하지 않는다.

## B. 정식 EXP Registry — 68 physical/version rows

### 도메인과 버전

- DRAW `53`
- CROWD `9`
- PRIZE `6`
- V1 `65`, V2 `3`

### 현재 Registry 상태 분포

- REGISTERED `36`
- DESIGNED `1`
- FAILED `9`
- FAILED_EARLY `8`
- FAILED_NOT_SUPPORTED `2`
- FAILED_NO_SELECTION_SIGNAL `1`
- SUPPORTED_WITHIN_EXPERIMENT `2`
- SUPPORTED_CROSS_OUTCOME `1`
- EXPLORATORY_NOT_SUPPORTED `1`
- EXPLORATORY_RETAILER_MODE_CONCENTRATION `1`
- OFFICIAL_REPAIR_APPLIED_AND_VERIFIED `1`
- READY_FOR_TEST `1` (EXP-018 V1 실행은 bootstrap ambiguity에서 outcome peek 0으로 차단)
- AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT `1`
- PROTOCOL_BLOCKED_SOURCE_SEMANTICS `1`
- PROSPECTIVE_LOCKED_WAITING_FOR_DATA `2`

### 최신 번호 연구

- EXP-017: `FAILED_NOT_SUPPORTED`; Development failure 뒤 Holdout 미실행, rescue 금지.
- EXP-018 V1: `EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY`; outcome peek 0, Registry schema status READY_FOR_TEST 보존.
- EXP-018 V2: `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
- EXP-019: `FAILED_NOT_SUPPORTED`; Holdout 미실행.
- EXP-020: `FAILED_NO_SELECTION_SIGNAL`; TRAIN positive bands 60, Selection eligible 0, Holdout 미실행.

Registry 행과 결과를 수정하지 않았다. 상세 ID·명칭·상태는 authoritative Registry 원문을 우선한다.

## C. EXP ID 없이 실제 계산·검증한 연구 — 27개 축

1. TRIO ORBIT Fixed/Linked 역사검증.
2. TRIO ORBIT divergence attribution.
3. KTS pair-completion collision.
4. LAG 3~6 reappearance map.
5. BONUS extinction interaction.
6. BONUS lag2 interaction.
7. Ending-frequency interaction.
8. TRIO HOLD causal decomposition.
9. Survivor-pool rolling-origin actionability.
10. Opposite-period stability filter validation.
11. NO-PICK structural root-cause audit.
12. NO-PICK causal trace.
13. NUMBER member-structure SEVERE causal trace.
14. Current-1239 END_DIGIT severe causal trace.
15. Current-1239 NUMBER/END_DIGIT root-cause trace.
16. Current-1239 opposite-period causal trace.
17. Current-1239 official pre-draw audit.
18. Contiguous 1..1238 rebuild and 1239 rerun.
19. Discovery 2.0 independent-signal audit.
20. Pair shadow repair deterministic validation.
21. Official repair Phase A/B canary/change-control validation.
22. Official repair apply/finalize verification.
23. Crowd topology 001 supporting audit lineage.
24. Crowd topology 002 independent reproduction/calibration.
25. Crowd topology 003 supporting methodology lineage.
26. Crowd retail 001 calibration/reproduction lineage.
27. Prize-share 001/002 historical validation 및 prospective preparation lineage.

여기서 Registry 정식 행 자체와 중복되는 결과를 새 formal row로 세지 않는다. 이 27은 Registry row count와 별도인 실제 검증·감사 축이다.

## D. UNEXECUTED / REVIEWED IDEA — 2개

|아이디어|상태|EVIDENCE_STATUS|
|---|---|---|
|MBC 실제 공 추첨순서 / DRAW-ORDER|정식 EXP 아님, 효과 검증 미실행, 선행연구 대비 가치가 낮아 보류. source feasibility 12/12만 확인.|`REVIEWED_IDEA / LOCAL_FEASIBILITY_EVIDENCE`|
|REHEARSAL / 리허설 번호|정식 EXP 아님, EXP-021 아님, 실행 안 함, 사용자 판단으로 패스.|`USER_DECISION / CONVERSATION_ORIGIN_IDEA / NO_RESULT_EXPECTED`|

REHEARSAL에 실행 결과가 없는 것은 오류가 아니다. 두 항목 모두 실행연구 통계와 `unsupported executed research`에서 제외한다.

## 현재 운영 상태

- NO-PICK: `867/867`, output 0, rate `100%`; 미해결.
- 1239 TRIO ORBIT prospective: sealed `PENDING`; historical 결과와 혼합 금지.
- 실패축 rescue 금지, 결과 전 protocol lock, sealed 원본 수정 금지.


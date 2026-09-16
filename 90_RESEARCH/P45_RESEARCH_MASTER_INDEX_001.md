# P45 전체 연구 마스터 인덱스 001

## 기준과 목적

- 기준일: `2026-08-28`
- P45는 번호 생성기가 아니라 구조·전이·관계·복귀·반대가설을 검증하는 숫자 연구소다.
- Official Engine은 `FROZEN`; 사용자 명시 승인 전 변경하지 않는다.
- `3/3=PRIMARY`, `exact 2/3=SUPPORT`; 혼합판정 금지.
- 증거 전수목록: `P45_RESEARCH_EVIDENCE_INVENTORY_001.csv` (`551` files).
- 정식 Registry 원문 snapshot: `P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv` (`53` physical/version rows). 기존 문서의 “68” 메모와 실제 표 행 수가 달라 실제 행을 우선한다.

## A. 공식 엔진 내부에서 연구·운영된 구조 — 12개

|구조|실제 의미와 상태|근거|
|---|---|---|
|UNIT_3|3단위 구간의 점유·전멸·복귀·조건부 성과. 실제 1239 predraw에서는 NORMAL 69.1188.|`docs/P45_v2.7_Web_UTF8_LF.md`, current-1239 rerun|
|UNIT_5|5단위 구간 연구. 과거 causal trace에서 SEVERE 99.1909였으나 contiguous 1..1238 재구축 후 1239 rerun은 NORMAL 57.4778.|number-member trace, current-1239 rerun|
|UNIT_9|9단위 전멸구간·복귀깊이 0/1/2·점유벡터. 1239 rerun NORMAL 62.4091.|v2.5/v2.7 원문, current-1239 rerun|
|UNIT_10|10단위 구간, 41..45 크기 보정 포함. 1239 rerun NORMAL 65.4002.|v2.7 원문, current-1239 rerun|
|END_DIGIT|끝수 점유·전멸·복귀. 1239 rerun에서는 SEVERE 100.0으로 NUMBER 차단 원인.|current-1239 rerun/root-cause trace|
|NUMBER|개별 번호 구조·멤버십 관문. 현재 1239 공식 pre-draw는 selected 0.|current-1239 rerun|
|TRIO|3개 조합이 핵심 연구 단위. `3/3 PRIMARY`, `exact2/3 SUPPORT`.|Core Guide 007|
|PAIR|PAIR lifecycle/signature/timing을 shadow repair 후 사용자 승인 change-control로 적용·검증.|pair shadow/official repair audits|
|CORE|NUMBER→TRIO→PAIR→CORE 보호 판정 계층. 임의 혼합·우회 금지.|Core Guide/official manifests|
|Fixed Orbit|고정 KTS 순서의 3×3 TRIO 대조군. 역사 exact3 5/1237.|TRIO ORBIT V1 result|
|Linked Orbit|직전 MAIN6+BONUS anchor 연동 3×3 TRIO. 역사 exact3 7/1237이나 우월성 미지지.|TRIO ORBIT V1/divergence result|
|KTS45|330 TRIO 고정 schedule. 결과 후 재생성 금지.|KTS schedule/protocol|

UNIT_5·UNIT_9·UNIT_10 전멸구간은 실제 설계 원문에 존재한다. UNIT_9는 v2.5에서 공식 전멸복귀 축으로 상세 구현됐고, UNIT_3/5/9/10은 v2.7에서 모두 독립 점유·전멸·복귀 계산 대상으로 확장됐다. 현재 상태는 과거 SEVERE trace와 contiguous 재구축 후 1239 rerun을 혼동하지 않는다.

## B. 정식 EXP 연구 — Registry 53행

모든 ID·명칭·상태는 `P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`에 전 행 보존한다. 아래는 사용자용 상태 분류다.

- 등록/미실행 또는 근거파일 미연결: 001, 003–009, 011, 014–016, 018–024, 027–037, 038-V1. 상태는 `REGISTERED/DESIGNED/HOLD/PARTIAL`; 실행 성공으로 해석하지 않는다.
- 실행 실패: 002(동시출현), 010(1-step transition), 012(격회 재출현), 013(같은 끝자리), 017(가변 전멸), 025(유사회차 전이), 026(간격), 038-V2(NO-PICK fallback).
- 조기 실패 settlement: 039 홀수 lag-1, 040 합계 lag-1, 041 미러 보수, 042 return-age, 043 누적빈도, 044 BONUS→MAIN, 045 BONUS 상대순위, 046 번호라벨 지속성.
- 공식 change-control audit: `EXP-DRAW-20260824-010-V1`, `OFFICIAL_REPAIR_APPLIED_AND_VERIFIED`; 일반 예측 EXP와 구분한다.
- EXP-017: TRIO ORBIT consensus number effect, `FAILED_NOT_SUPPORTED`; Development hits 224/1592, exact p `0.19907501596738386`, Holdout 미실행, rescue 금지.
- EXP-018 V1: adjacency residual effect, bootstrap U95 정의 모호성으로 `EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY`, outcome peek 0.
- EXP-018 V2: `T-1 MAIN6 → numerical ±1 adjacency → T MAIN6`, 양 split 실용효과 없음으로 `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
- EXP-019: sales-adjusted birthday-range crowd effect, beta `0.011148559895275412`, p `0.22829771702282978`, `FAILED_NOT_SUPPORTED`, Holdout 미실행, rescue 금지.
- EXP-020: lagged winner-count regime signal, TRAIN positive bands 60, Selection eligible 0, `FAILED_NO_SELECTION_SIGNAL`, Holdout 미실행, rescue 금지.

각 초기 EXP의 연구질문은 Registry의 한글 이름 자체를 기준으로 하며, Development/Holdout 수치가 원문에 없는 등록-only 행은 `근거미확인/미실행`으로 남긴다.

## C. EXP 번호 없이 실제 계산·검증한 연구 — 27개 축

1. TRIO ORBIT Fixed/Linked 역사검증 — exact3 5 vs 7, 원 판정 `FAILED_NOT_SUPPORTED`.
2. TRIO ORBIT divergence attribution — 차이 +2, paired p `0.386906131`, `DIVERGENCE_NOT_SUPPORTED`.
3. KTS pair-completion collision — `FAILED_NOT_SUPPORTED`.
4. LAG 3~6 reappearance map — 결과파일 보존, 독립 상호작용 지도.
5. BONUS extinction interaction — EXP-004×EXP-015 결합 검증.
6. BONUS lag2 interaction — EXP-005×EXP-015 결합 검증.
7. Ending-frequency interaction — EXP-006×EXP-013 결합 검증.
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
19. Discovery 2.0 independent-signal source audit.
20. Pair shadow repair deterministic validation.
21. Official repair Phase A/B canary/change-control validation.
22. Official repair apply/finalize verification.
23. Crowd topology 001.
24. Crowd topology 002 + independent reproduction/calibration.
25. Crowd topology 003.
26. Crowd retail 001 + calibration/reproduction.
27. Prize-share 001/002 historical validation 및 prospective preparation.

각 축의 상세 verdict와 수치는 evidence inventory의 실제 result/audit/calculation 파일을 우선한다. 운영 repair audit은 예측 신호 연구와 섞지 않는다.

## D. 아이디어 검토만 하고 정식 실행하지 않은 후보 — 2개

- 실제 공 추첨순서/MBC draw order: source feasibility는 공식 MBC 표본 12/12 추출 가능으로 확인됐지만 정식 EXP 등록·효과 검증은 하지 않았다. 현재 우선순위 보류.
- REHEARSAL/리허설 번호: 정식 EXP-021 아님, 미실행·패스. 로컬 독립 결정문 근거는 `근거미확인`이며 사용자 지시 상태만 보존한다.

## 폐쇄축·미해결·prospective

- 폐쇄축: EXP-018 V2의 `T-1 MAIN6 → numerical ±1 adjacency → T MAIN6`.
- NO-PICK: `VALID_ROUNDS=867`, `OUTPUT_AVAILABLE_ROUNDS=0`, `RESEARCH_NO_PICK_ROUNDS=867`, `NO_PICK_RATE=100%`; 미해결.
- 1239 TRIO ORBIT prospective: sealed `PENDING`; Fixed `9-38-40 / 11-13-27 / 12-41-43`, Linked `11-38-44 / 3-39-42 / 2-13-30`; 역사검증과 혼합 금지.
- 다음 원칙: 실패축 rescue 금지, 새 독립가설은 결과 전에 별도 protocol lock, 1239 결과 전 sealed 원본 수정 금지.

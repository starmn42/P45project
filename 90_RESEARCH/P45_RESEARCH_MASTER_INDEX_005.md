# P45 전체 연구 마스터 인덱스 003

## 문서 지위와 복구 순위

- 기준일: `2026-09-01`
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
|EXP 외 실제 연구|28|정식 canonical Registry ID 없이 계산·검증된 연구 축|
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

## C. EXP ID 없이 실제 계산·검증한 연구 — 28개 축

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
28. LZ76 거시 복잡도 국면 고립 검정 V1 — `FAILED_NOT_SUPPORTED`; occupancy p1 `0.014598540145985401` PASS, persistence p2 `0.43745625437456254` FAIL, joint `NO`, reproducibility `PASS`, future leakage `0`.

여기서 Registry 정식 행 자체와 중복되는 결과를 새 formal row로 세지 않는다. 이 27은 Registry row count와 별도인 실제 검증·감사 축이다.

## D. UNEXECUTED / REVIEWED IDEA — 2개

|아이디어|상태|EVIDENCE_STATUS|
|---|---|---|
|MBC 실제 공 추첨순서 / DRAW-ORDER|정식 EXP 아님, 효과 검증 미실행, 선행연구 대비 가치가 낮아 보류. source feasibility 12/12만 확인.|`REVIEWED_IDEA / LOCAL_FEASIBILITY_EVIDENCE`|
|REHEARSAL / 리허설 번호|정식 EXP 아님, EXP-021 아님, 실행 안 함, 사용자 판단으로 패스.|`USER_DECISION / CONVERSATION_ORIGIN_IDEA / NO_RESULT_EXPECTED`|

REHEARSAL에 실행 결과가 없는 것은 오류가 아니다. 두 항목 모두 실행연구 통계와 `unsupported executed research`에서 제외한다.

## 현재 운영 상태

- NO-PICK: `867/867`, output 0, rate `100%`; 미해결.
- 1239 TRIO ORBIT prospective: sealed original `UNCHANGED`, separate settlement `COMPLETE`; Fixed PRIMARY/SUPPORT `0/1`, Linked PRIMARY/SUPPORT `0/0`. Historical 결과와 혼합 금지.
- 실패축 rescue 금지, 결과 전 protocol lock, sealed 원본 수정 금지.

## WHOLE-ENGINE synthetic replay semantics recovery audit

- EXP-035 fair-null attempt: `STOP_NULL_SEMANTICS_NOT_VALID`; B=`0/2000`; hypothesis=`NOT_EVALUATED`.
- 기존 baseline 재사용: exact valid targets `369..1235 / 867`, output `0`, no-pick `867`.
- lifecycle feasibility: `SEMANTICS_RECOVERED_EXISTING`; 승인된 repair semantics 외 새 규칙 추가 `NO`.
- canonical sandbox TRIO rebuild: 1,193 rounds 및 100,711 deterministic exposures exact equality `PASS`.
- PAIR target 662에서 retained authoritative historical placeholder state와 repaired-from-scratch state가 불일치.
- final: `SEMANTICS_REBUILD_NOT_EQUIVALENT`; 결과를 보고 규칙 수정 `NO`; 035 simulation 미실행.
- Registry 035/036/037 `REGISTERED` 유지; `REGISTRY_STATUS_UPDATE_NOT_CONFIRMED`.
- executed count `27` 유지; 이 audit로 completed/executed count 증가 없음.
- evidence: `v27_storage/audits/whole_engine_synthetic_replay_semantics_recovery_001`.

## 운영 후속 — WEB 자동 lifecycle 및 1240→1241 전환

- 연구 verdict 또는 Registry 행의 변경이 아닌 운영/표시 후속 작업이다.
- 1240 canonical official result 반영 및 prospective settlement 완료.
- 1241 prospective는 결과 확인 전에 preview/seal 되었으며 current PENDING이다.
- 웹 시작 시/주기 확인으로 `결과 감지 → canonical → settlement → next preview/seal → projection` lifecycle을 연결했다.
- 중복 실행은 `DRAW_ALREADY_CURRENT`에서 write 없이 종료됨을 SHA 비교로 확인했다.
- Official Engine semantics 변경 0, future leakage 0.
- evidence: `v27_storage/audits/web_finalization_auto_update_ui_001`.

## 2026-09-06 — P45 JOSEON HERITAGE UI Work (시안 비교 대기)

- 이 추가 기록이 앞선 과거 회차/WEB 문구보다 현재 상태에 우선한다. 역사 기록은 삭제하지 않음.
- WEB DESIGN = P45 JOSEON HERITAGE, IMPLEMENTED. Previous CONCEPT03 neon direction = SUPERSEDED.
- 현재 메뉴 = 홈 / 미래검증 기록 / 안전 점검.
- HOME = 신규회차 추천픽 우선 / 지난회차 검수 보조. 두 상세는 홈 상단 버튼으로 진입.
- 현재 1240 settlement COMPLETE, 1241 PENDING / SEALED, future leakage 0. sealed/canonical 등 21개 대상 변경 전후 SHA 동일.
- 신규회차 상세 = 결과 대기 중 / 적중표시 없음. 지난회차 상세 = 결과·적중 검수 표시.
- Desktop 1366/1440, mobile 390/412/430, drawer 및 두 상세를 실제 rendered screenshot으로 확인. 총 23개 캡처 경계 검사: horizontal overflow 0, console errors 0.
- REFRESH_ROLE = REMOVED_REDUNDANT. 기존 load()는 /api/status 조회만 수행. 최초 load() 및 backend 300초 auto lifecycle은 unchanged. 기존 frontend polling 없음; 추가하지 않음.
- 이전 인수인계 판정: PASS_WEB_UI_DESKTOP_MOBILE_FINAL → PASS_WEB_UI_HOME_FINAL → PASS_WEB_HOME_NAV_FINAL; desktop/mobile responsive PASS; auto update PASS. 이는 전달된 역사적 판정이며 이번 조선풍 최종 승인으로 대체하지 않음.
- 현재 최종 UI 판정 = IMPLEMENTED_AND_VERIFIED_REFERENCE_COMPARISON_PENDING. 승인 시안 이미지가 없어 PASS_WEB_JOSEON_HERITAGE_FINAL 미발급.
- Evidence = E:\P45 프로젝트\v27_storage\audits\web_joseon_heritage_001\FINAL_REPORT.md, browser_checks.json, protected_comparison.json, screenshots/*.png.
- RESUME_FROM = APPROVED_REFERENCE_COMPARISON_ONLY. 승인 시안과 기존 캡처 비교부터 재개; 완료된 전체 검증/정산/생성 반복 금지.
- Official Engine FROZEN; NO-PICK 867/867 UNRESOLVED; latest numbered EXP-020; EXP-035 NOT_EVALUATED / STOP_NULL_SEMANTICS_NOT_VALID. 연구/Registry 수 변화 없음.


## 2026-09-30 — EDGE ARITHMETIC FAMILY V1

- Canonical ID EXP-DRAW-20260930-001-V1, direct duplicate NEW. Four formulas ×2lags, MAIN-only primary, no rule tuning.
- Family NO_SUPPORTED_ENDPOINT; six INCONCLUSIVE positive effects, two FAILED_NOT_SUPPORTED (A2/D1), no SUPPORTED endpoint.
- Completed1..1243; locked 70/30 per lag;5 blocks;50,000 full-record order permutations,8 endpoint maxT, exact independent reproduction PASS.
- Research runner idempotent, repeat write0; all4 research shadow source1243 ->1244/1245 sealed. Official integration NO; promotion false; Official/DB/sealed/prospective/WEB change0; leakage0.
- Formal rows69 (DRAW54/CROWD9/PRIZE6). Latest numbered EXP-020 unchanged. Prior Recovery043 remains authoritative for runtime/UI state; this Work did not revalidate WEB.
- Evidence: v27_storage/experiments/edge_arithmetic_family_v1_001/final_result.md; protocol.json; reproducibility_report.json; protection_comparison.json.


## 2026-09-30 — TRIO ORBIT RETROSPECTIVE + AUTO RESEARCH LOOP V1

- 새 운영 원칙: "매 공식 결과 settlement 후 active research 자동 retrospective를 수행하고, 안전한 follow-up candidate를 자동 평가한다."
- TRIO ORBIT Prospective(1239..1243, 5회): Fixed PRIMARY 0, Linked PRIMARY 0, Fixed SUPPORT 3, Linked SUPPORT 1.
- Null Calibration: 3개 TRIO 후보 제시 시 공정 6/45 추첨에서 1회차당 적어도 1개 SUPPORT(exact 2/3) 발생 확률은 약 12.12%. N=5 표본은 SMALL_SAMPLE_INCONCLUSIVE이며 60% 성능으로 과대평가 불가.
- Historical(1..1238, 1,237회): Fixed PRIMARY 5/1237 (0.40%), Linked PRIMARY 7/1237 (0.57%), McNemar p=0.77441; Fixed SUPPORT 159/1237 (12.85%), Linked SUPPORT 174/1237 (14.07%), McNemar p=0.41025. Anchor 재출현 36.54% vs 귀무 35.60% (p=0.49). 우월성 증거 없음 (NO_EVIDENCE_OF_LINKED_SUPERIORITY).
- Official Engine: NO_CHANGE_SUPPORTED. 엔진 코드/게이트/DB 수정 0건 (FROZEN 유지).
- WEB 의미론: web/index.html의 "직전연동 V1 · 실전 우선"은 증거와 불일치하여 SEMANTIC_MISMATCH_CANDIDATE로 기록. 권장 "직전연동 V1 · 연구 비교" 제안 (실제 WEB 수정 0).
- AUTO RESEARCH LOOP V1: src/p45_v27/research_automation/ 구현 완료. 공식 lifecycle 격리, Promotion Firewall, 사후 데이터 오염 방지, 프로토콜 사전잠금, 멱등성 보장, 17개 단위/통합 테스트 PASS.
- Registry: 69 rows 유지 (인프라 구현 자체는 새 예측 실험으로 카운트하지 않음, latest numbered EXP-020 유지).
- Evidence: v27_storage/audits/trio_orbit_prospective_retrospective_001/ 및 v27_storage/research_automation/.


## 2026-09-30 — STATISTICAL CORRECTION + RESEARCH DISCOVERY AGENT V1

- **PHASE A (통계 정정 및 계보 보존):**
  - Prospective Fixed SUPPORT: 기존 보고된 p≈0.0137은 단일 점확률 PMF $P(X=3) \approx 0.013757$이었음을 확인. 정확한 단측 농축 p-value $P(X \ge 3) \approx 0.014733$ 및 양측 exact binomial $p \approx 0.014733$으로 정정. Wilson 95% CI: [0.2307, 0.8824], $N=5$ 극소 표본으로 `SMALL_SAMPLE_INCONCLUSIVE`.
  - Historical Linked SUPPORT: $N=1237, k=174$ (기대치 149.96)에 대해 단측 $p \approx 0.021781$, 양측 $p \approx 0.040486$. 본 분석은 사후 탐색적 진단(`RETROSPECTIVE_NOMINAL_DEVIATION` / `NOMINAL_SIGNAL_ONLY`)이며, 4대 역사 귀무검정군에 대해 Holm 다중비교 감도 보정 적용 시 $p_{\text{adj}} \approx 0.087125$ ($> 0.05$)로 가족별 유의성 미도달.
  - Paired Direct Comparison: Fixed vs Linked 대응표본 검정(Both=22, Fixed-only=137, Linked-only=152, Neither=926)에서 McNemar exact $p = 0.410251$로 우월성 없음 (`NO_EVIDENCE_OF_LINKED_SUPERIORITY` 확정 유지).
  - Linked Anchor Recurrence: 관측 36.54% vs 공정 귀무 35.60% ($Z=0.69, p=0.48912$). 추가 정보량 없음 (`NO_INCREMENTAL_ANCHOR_EVIDENCE` 확정 유지).
  - 계보 보존 증거: `v27_storage/audits/trio_orbit_prospective_retrospective_001/TRIO_ORBIT_STATISTICAL_CORRECTION_001.md`, `.json` 생성 및 보고서 전면 반영.

- **PHASE B (핵심 판정 재확인):**
  - Official Engine: `NO_CHANGE_SUPPORTED` (엔진/임계치/게이트/DB 수정 0건, FROZEN 유지).
  - Fixed vs Linked: `NO_EVIDENCE_OF_LINKED_SUPERIORITY`.
  - Linked Anchor: `NO_INCREMENTAL_ANCHOR_EVIDENCE`.

- **PHASE C (P45 RESEARCH DISCOVERY AGENT V1 구현 및 가동):**
  - 구현 위치: `src/p45_v27/research_automation/` 하위 6대 신규 모듈 (`research_ontology.py`, `research_coverage_map.py`, `coverage_gap_analyzer.py`, `novelty_checker.py`, `idea_quality_gate.py`, `idea_provider.py`, `candidate_ranker.py`, `research_discovery_agent.py`).
  - 24대 연구 개념축 Ontology 정의 및 연구 커버리지 맵 생성 (`RESEARCH_COVERAGE_MAP.json`).
  - 사후 결과 스캔/적중률 브루트포스 절대 금지: 오직 구조적 공백(STRUCTURAL_GAP, NEGATIVE_SPACE, OPPOSITE_HYPOTHESIS, CROSS_STRUCTURE) 기반 탐색.
  - 10대 Idea Quality Gate (NOVEL, NON_RESCUE, FALSIFIABLE, CLEAR_OPPOSITE, NULL_DEFINED, FUTURE_TESTABLE, DATA_AVAILABLE, MIN_SAMPLE_DEFINABLE, NO_LEAKAGE, MULTIPLE_TESTING_CONTROLLABLE) 구현.
  - 제공자 구조: `DeterministicStructuralProvider` (ACTIVE), `OptionalLLMIdeaProvider` (`NOT_CONFIGURED` - 안전하게 비밀키 요구/생성 없이 정상 스탠바이).
  - 첫 Discovery Cycle (1243회 대상 1회 실행):
    - `IDEA-1243-NEGA-001`: Fixed-Partition Extinction Negative-Space Recovery Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
    - `IDEA-1243-OPPO-002`: Number Proximity Minimum-Distance Repulsion Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
    - `IDEA-1243-CROS-003`: Pair Lifecycle Dormancy Duration Geometric Memory Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
    - 멱등성 검증 완료: 동일 1243회 재호출 시 new candidates = 0, duplicate write = 0.
  - Official Firewall: `PROMOTION_CANDIDATE` -> `USER_APPROVAL_REQUIRED` 자동 차단 유지.
  - 검증 및 회귀테스트: 29 tests PASS (기존 17개 + 신규 12개 통계정정/디스커버리 에이전트).
  - Official 보호 검증: 13대 공식 자산 변경 0건 (`Protection verdict: PASS, Changed: 0`), future leakage = 0.


## 2026-09-30 — RESEARCH DISCOVERY AGENT V1.1 (SEMANTIC DUPLICATE GUARD + RUNTIME/GIT FINALIZATION)

- **배경 및 V1 근본 원인 분석:**
  - V1 Novelty Checker가 단순 문자열/키워드 매칭(exact substring)에 의존하여, 구조적 동등성을 지닌 과거 연구(EXP-004 가변 전멸구간, EXP-015 결손 회복속도, EXP-018 인접 쌍, EXP-027 간격 분산 등)를 신규 후보로 잘못 통과시키는 취약점이 발견됨.
  - Coverage Map에서 개념 공간 차원(24대 Ontology 축)과 각 축에 매핑된 연구 인스턴스들의 상태 카운트(Tested, Active, Failed 등)를 혼동하여 총합 불일치 발생.
  - 프로토콜 잠금(Protocol Lock) 및 미래 봉인(Prospective Seal) 완료 전 후보 생성 단계에서 `confirmatory_start_round`가 조기 확정되어 누수 위험 구조가 존재함.
- **V1.1 구조적 개선 사항:**
  1. **RESEARCH KNOWLEDGE INDEX 기계 판독 체계 구축 (`knowledge_index.py`):**
     - 공식 Registry 69행 + 비-EXP 실행 연구축 3건 + Official 내부 연구축 5건 등 총 77건의 정규화된 연구 레코드 색인 (`RESEARCH_KNOWLEDGE_INDEX.json`). 8대 핵심 구조 필드(INPUT, TRANSFORMATION, CONDITION, TARGET, LAG, METRIC, NULL, ACTIONABILITY) 완비.
  2. **COVERAGE MAP V1.1 정밀화 (`coverage_map_v1_1.py`):**
     - 24대 불변 온톨로지 개념축과 비배타적 연구 상태 카운트를 분리. 역추적 가능한 research_id 매핑 완비 (`len(axes) == 24`, 불변 검증 PASS).
  3. **SEMANTIC NOVELTY CHECKER V1.1 (`semantic_novelty_checker.py`):**
     - 모든 신규 후보에 대해 기존 연구 77건 대상 8차원 구조 비교 수행 및 유사도 Top 10 산출.
     - 중복 유형 분류: `EXACT_DUPLICATE`, `NEAR_DUPLICATE`, `FAILED_AXIS_RESCUE`, `PARTIAL_OVERLAP`, `DISTINCT`.
     - 증거 산출물 필수화: `CANDIDATE_NOVELTY_EVIDENCE.json`, `.md` 생성 없이는 프로토콜 준비 불가.
  4. **READY_FOR_PROTOCOL 게이트 강화 (`idea_quality_gate.py`):**
     - 10대 기본 품질 게이트 통과 외에 4대 시맨틱 게이트(`SEMANTIC_DUPLICATE_CHECK`, `FAILED_AXIS_RESCUE_CHECK`, `NOVELTY_EVIDENCE_EXISTS`, `NOVELTY_JUSTIFICATION`) 전수 PASS 필수화.
  5. **확증 회차(Confirmatory Round) 2단계 안전 분리:**
     - 후보 제안 시점: `earliest_eligible_confirmatory_round = 1244`만 기록, `confirmatory_start_round = None` 강제.
     - 프로토콜 잠금, SHA-256 생성, 봉인 완료 및 당첨 미공개 시점에만 실제 확증 시작 회차 확정 (Future Leakage = 0).
- **V1 3대 후보 재평가 결과:**
  - 후보 A (`IDEA-1243-NEGA-001` - Fixed-Partition Extinction Negative-Space Recovery Invariance):
    - Top Similar: EXP-015 (결손 회복속도), EXP-004 (가변 전멸구간, FAILED), EXP-022 (이동×가변 전멸 교차).
    - 판정: **`REJECT_RESCUE`** (기존 실패/등록된 전멸·복귀 축의 사후 재포장으로 판명).
  - 후보 B (`IDEA-1243-OPPO-002` - Number Proximity Minimum-Distance Repulsion Invariance):
    - Top Similar: EXP-027 (간격 분산), EXP-018 (인접 번호 구조, CLOSED), EXP-008 (숫자 간격 구조).
    - 판정: **`REJECT_RESCUE`** (기존 종결된 간격/인접 번호 축의 명칭 변경으로 판명).
  - 후보 C (`IDEA-1243-CROS-003` - Pair Lifecycle Dormancy Duration Geometric Memory Invariance):
    - Top Similar: EXP-012 (PAIR 2회 출현 주기 및 갭 분석), Official Pair Lifecycle Repair.
    - 판정: **`NEEDS_EVIDENCE`** (공식 무결성 점검과 개념적 차이는 인정되나, 990개 페어에 대한 사전 다중가설군 및 위험률 풀링 증거 미비로 보류).
  - 생존 후보: **0건** (`NO_VALID_NEW_HYPOTHESIS`). 억지 후보 통과 0건.
- **테스트 및 검증:**
  - 단위/통합/회귀 테스트: 총 44개 테스트 전수 통과 (Auto Research Loop 17 + Discovery V1 12 + Discovery V1.1 15, 0 failures, 0 errors).
  - 공식 엔진 보호: 13대 공식 자산 무결성 100% 유지 (`Protection verdict: PASS, Changed: 0`).
  - 로컬 런타임 활성화: `ResearchAutomationCoordinator` 초기화 및 V1.1 시맨틱 가드 활성 확인 완료.
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.
  - 정식 레지스트리: 69행 유지 (새 실험 실행 0건).


## 2026-09-30 — RESEARCH DISCOVERY AGENT V1.2 (KNOWLEDGE COVERAGE COMPLETION & FAIL-CLOSED FINALIZATION)

- **배경 및 V1.1 원인 분석 (Coverage Gap Resolution):**
  - 직전 V1.1 보고에서 Knowledge Index가 77건(Formal 69, Non-EXP 3, Official 5)으로 집계되었으나, authoritative Research Master에는 EXP ID 없이 실제 실행·검증한 Non-EXP 연구축(최소 28건 + 후속 감사 3건 = 31건)과 Official Internal 연구축(12건)이 실존함.
  - V1.1에서는 대표 축 3개/5개만 직접 색인하고 나머지를 누락하였던 구조적 공백이 확인됨.
  - 성공 기준 `KNOWN_RESEARCH_SOURCE_COVERAGE = 100%`, `UNEXPLAINED_MISSING_SOURCE_ITEMS = 0` 달성을 위해 전체 원천 연구 전수 색인 및 기계적 증명 체계 구축.
- **V1.2 핵심 구현 및 구조적 성과:**
  1. **원문 기반 SOURCE INVENTORY 구축 (`knowledge_source_inventory.py`):**
     - 임의 축약/추측 배제, 원천 문서(P45_RESEARCH_MASTER_INDEX_005.md, 06_INITIAL_EXPERIMENT_REGISTRY.md 등) 파서를 통해 총 115건의 원천 연구 항목 수집:
       - `FORMAL_REGISTRY`: 69건 (DRAW 54, CROWD 9, PRIZE 6)
       - `NON_EXP_EXECUTED`: 31건 (Section C 28건 + 후속 감사 3건)
       - `OFFICIAL_INTERNAL`: 12건 (UNIT_3, UNIT_5, UNIT_9, UNIT_10, END_DIGIT, NUMBER, TRIO, PAIR, CORE, Fixed Orbit, Linked Orbit, KTS45)
       - `REVIEWED_UNEXECUTED`: 2건 (MBC DRAW-ORDER, REHEARSAL)
       - `ACTIVE_PROSPECTIVE`: 1건 (1244회 봉인 TRIO ORBIT)
     - 산출물: `RESEARCH_SOURCE_INVENTORY.json`, `RESEARCH_SOURCE_INVENTORY.md` 저장 완료.
  2. **100% 완결 COVERAGE MANIFEST (`RESEARCH_KNOWLEDGE_COVERAGE_MANIFEST.*`):**
     - 모든 원천 항목에 대해 정규화 레코드 매핑 생성 (Mapped: 115 / 115, 100.0%, Unmapped: 0).
     - 매핑 유형: DIRECT 107건, ALIAS 6건 (동일 실체 감사 계보), MERGED 2건 (EXP-009 단일 실체 카나리/검증 통합), RELATED_DISTINCT 0건.
     - 임의 병합 금지: 명확한 증거(Evidence)와 사유(Reason)가 입증된 경우에만 ALIAS/MERGED 승인.
  3. **KNOWLEDGE INDEX V1.2 정규화 및 양방향 역추적 (Reverse Trace):**
     - 총 107건의 정규화 레코드(`RESEARCH_KNOWLEDGE_INDEX.json`, `RESEARCH_KNOWLEDGE_INDEX.md`).
     - 오래된 연구의 미상 필드는 추측 없이 `UNKNOWN` 유지 (레코드 탈락 방지).
     - 양방향 역추적 무결성: `Source Item -> Record` (115/115 PASS), `Record -> Source Items` (107/107 PASS).
  4. **FAIL-CLOSED 차단 모드 가동 (`research_discovery_agent.py`):**
     - `knowledge_coverage_complete != True` 시 즉시 `BLOCKED_KNOWLEDGE_COVERAGE_INCOMPLETE` 반환, 신규 후보 생성 및 프로토콜 승격 완전 차단.
  5. **COVERAGE MAP V1.2 온톨로지 연동:**
     - 24대 불변 온톨로지 축과 107개 정규화 레코드 연동 완료, 고아 레코드(Orphan) = 0건 검증 완료.
- **후보군 A/B/C 전체 Index 재검증 (Regression Verdict):**
  - 후보 A (`IDEA-1243-NEGA-001`): `REJECT_RESCUE` 유지 (기존 실패 전멸·복귀 축 구제 시도 차단).
  - 후보 B (`IDEA-1243-OPPO-002`): `REJECT_RESCUE` 유지 (기존 종결 간격 분산 축 구제 시도 차단).
  - 후보 C (`IDEA-1243-CROS-003`): `NEEDS_EVIDENCE` 유지 (READY_FOR_PROTOCOL 자동 승격 금지, 새 실험 실행 0건).
  - 전체 신규 후보 생성: 0건 (`NO_VALID_NEW_HYPOTHESIS`).
- **테스트 및 검증:**
  - 20대 신규 테스트 스위트(`test_knowledge_coverage_completion.py`) 전수 통과.
  - 기존 44개 테스트 포함 총 64개 테스트 전수 통과 (0 failures, 0 errors).
  - 공식 자산 무결성 100% 보호 (`Protection verdict: PASS, Changed: 0`).
  - 로컬 런타임 활성화: V1.2 Fail-Closed Knowledge Coverage Guard 완전 장착 완료.
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.
  - 정식 레지스트리: 69행 유지 (새 실험 실행 0건).





- **2026-09-30: [CANONICAL RESEARCH ID RESOLVER + REFERENTIAL INTEGRITY FINALIZATION]**
  - **작업 목적:** 연구 색인 과정에서 발생할 수 있는 식별자 네임스페이스 혼동 및 잘못된 정식 레지스트리 ID ALIAS/MERGE를 원천 차단하고 참조 무결성(Referential Integrity) 기계적 보장 체계 구축.
  - **식별된 핵심 문제 및 원인:**
    1. EXP-009 (인간 레이블 / 홀수 lag-1 공분산)와 EXP-DRAW-20260816-009-V1 (물리 레지스트리 9행 / NUMBER RELATION LAB '전체 관계망')의 숫자 서픽스 자동 동일시 오류 가능성.
    2. 공식 PAIR 라이프사이클 수리 정식 레지스트리 행은 EXP-DRAW-20260824-010-V1 (OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT 001)임에도 오매핑될 위험.
    3. 후보 A top semantic match에 무관한 EXP-DRAW-20260821-042-V1 (RETURN LAB 개별 숫자 return-age rank) 유입 문제.
  - **구조적 해결 및 구현 성과:**
    1. **독립 모듈 구현 (canonical_id_resolver.py):**
       - 5대 식별자 네임스페이스 분리: CANONICAL_REGISTRY_ID, HUMAN_EXP_LABEL, NON_EXP_ID, OFFICIAL_INTERNAL_ID, SOURCE_ITEM_ID.
       - 서픽스 자동 매핑 엄격 금지 (EXP-009 != ...-009-V1).
       - 자동 생성 테이블: CANONICAL_REGISTRY_LOOKUP.json (69행), HUMAN_EXP_LABEL_MAP.json (28개 명시적 레이블).
    2. **전체 115개 원천 항목 및 ALIAS/MERGE 전수 감사:**
       - 산출물: RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.json, RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.md.
       - 결과: 정식 레지스트리 참조 74건 전수 해결 (무효 0, 모호 0), ALIAS 6건 전수 VALID, MERGED 2건 전수 VALID.
       - PAIR 수리 항목(SRC-NONEXP-20, 21, 22) 정규화 타깃을 EXP-DRAW-20260824-010-V1로 정정.
       - EXP-DRAW-20260816-009-V1 (전체 관계망) 및 EXP-DRAW-20260821-042-V1 (return-age rank) 보호 완료.
    3. **Fail-Closed 참조 무결성 가드 및 시맨틱 매처 정밀화:**
       - 상위 시맨틱 매칭에 무효/모호 레지스트리 참조 유입 시 BLOCKED_REFERENTIAL_INTEGRITY로 차단.
       - 동일 도메인이 아닌 경우 실패 축 구제(FAILED_AXIS_RESCUE) 분류 금지 -> 후보 A에서 무관한 return-age 오매칭 원천 배제.
    4. **후보군 A/B/C 재평가:**
       - 후보 A: REJECT_RESCUE (042 제외, EXP-004/015/022 기준 차단).
       - 후보 B: REJECT_RESCUE (간격·반발 실패축 기준 차단).
       - 후보 C: NEEDS_EVIDENCE (공식 PAIR 라이프사이클 및 010 수리 감사행 기준 유지, 프로토콜 승격 금지).
  - **테스트 및 검증:**
    - 22개 신규 테스트(test_canonical_id_integrity.py) 전수 통과.
    - 기존 64개 포함 총 86개 테스트 전수 통과 (0 failures, 0 errors).
    - 공식 엔진/DB/봉인 파일 변경 0건 (Protection verdict: PASS, Changed: 0).
    - Vercel 배포 불필요 (VERCEL_DEPLOY_NOT_REQUIRED).

- **2026-09-30: [NON-EXP 1:1 LINEAGE & SEMANTIC REFERENTIAL INTEGRITY FINAL PASS]**
  - **작업 목적:** NON-EXP source item 각각이 실제로 그 연구의 정식 formal experiment / lineage에 연결되어 있는지 전수 1:1 감사하고, 도메인 불일치 및 침묵의 오매핑(silent wrong alias)을 원천 차단하는 Domain Compatibility Hard Guard 구축.
  - **정정 및 구현 성과:**
    1. **Authoritative Canonical ID 정정:**
       - SRC-NONEXP-23: EXP-CROWD-20260823-005-V1 (EXP-CROWD-TOPO-001-V1, Row 58) 1:1 ALIAS 매핑.
       - SRC-NONEXP-24: EXP-CROWD-20260823-006-V1 (EXP-CROWD-TOPO-002-V1, Row 59) 1:1 ALIAS 매핑 (독립 재현 및 calibration 감사 계보 증빙).
       - SRC-NONEXP-25: EXP-CROWD-20260823-007-V1 (EXP-CROWD-TOPO-003-V1, Row 60) 1:1 ALIAS 매핑.
       - SRC-NONEXP-26: EXP-CROWD-20260823-008-V1 (EXP-CROWD-RETAIL-001-V1, Row 61) 1:1 ALIAS 매핑.
       - SRC-NONEXP-27: 다중 대상 계보 (EXP-PRIZE-20260816-001-V2, EXP-PRIZE-20260821-004-V1, EXP-PRIZE-20260821-005-V1)를 갖는 VALID_RELATED_DISTINCT 및 lineage_targets: [] 스키마 지원.
    2. **Domain Compatibility Hard Guard 장착:**
       - CROWD 소스는 반드시 CROWD 정식 대상에만 매핑 허용 (명시적 교차 증거 없는 한 DRAW/PRIZE 타깃 즉시 차단).
       - 위반 시 DOMAIN_MISMATCH_UNJUSTIFIED 및 FAIL_NON_EXP_REFERENTIAL_INTEGRITY로 Fail-Closed 발동.
    3. **후보군 A/B/C 정밀 재평가:**
       - 후보 A: REJECT_RESCUE 유지 (전멸·복귀 실패축 기준 차단).
       - 후보 B: REJECT_RESCUE 유지 (간격·인접 실패축 기준 차단).
       - 후보 C: NEEDS_EVIDENCE 유지 (무관한 쌍둥이 유사 회차 제거 완료, 공식 PAIR 라이프사이클 및 010 수리 행, KTS pair completion 기준 상위 매칭 재구성, 자동 승격 0).
    4. **무결성 판정:** PASS_NON_EXP_REFERENTIAL_INTEGRITY 복구 완료.

- **2026-09-30: [MASTER SOURCE IDENTITY LOCK & INVENTORY FINGERPRINT FINAL AUDIT]**
  - **작업 목적:** 이전 단계에서 발생한 연구명 임의 치환(예: "Number order statistical distribution", "Consecutive number adjacency structure" 등 합성 영문명 주입)을 완전히 근절하고, `90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md` Section C ("## C. EXP ID 없이 실제 계산·검증한 연구 — 28개 축") 원문을 단일 진실 원천(Single Source of Truth)으로 삼아 1:1 불변의 exact identity를 기계적으로 잠금(Lock).
  - **식별된 원인 (Root Cause):**
    - 이전 인벤토리 생성 보고에서 Section C의 한국어 실제 연구 원문 대신, 영문 합성/플레이스홀더 연구명이 임의 치환되어 주입되었음.
    - Section C는 실제 28개 축이며, 이후 추가된 3건의 감사 연구(WHOLE-ENGINE, TRIO ORBIT 회고, TRIO ORBIT 통계교정)가 Section C에 무리하게 병합되어 31개로 하드코딩되었던 결함 발견.
  - **정정 및 구현 성과:**
    1. **독립 1차 원문 추출기 (`MasterSourceRawExtractor`):**
       - 기존 인벤토리/지식 빌더 모듈과 일체의 함수/변수를 공유하지 않는 독립 Raw Parser 구축.
       - Section C 시작과 끝 사이의 28개 항목을 번역/요약/치환 없이 있는 그대로 추출하여 `MASTER_NON_EXP_RAW_SNAPSHOT.json` 및 `.md` 생성.
       - 각 항목 SHA-256 fingerprint 및 전체 섹션 결합 SHA-256 fingerprint (`66baf18efd12f9ad6d1a6e9f5e80422a5cfe9539025937b5a7e77bbc39a2b6bf`) 산출 및 `MASTER_NON_EXP_SOURCE_FINGERPRINTS.json` 영구 보존.
    2. **출처 분류 체계 분리:**
       - Section C 순수 28개 축은 `NON_EXP_EXECUTED` (28건)로 1:1 고정.
       - 이후 3건의 실동 감사는 `SourceClass.OTHER_RESEARCH_SOURCE` (3건: `SRC-OTHER-01` ~ `SRC-OTHER-03`)로 정당 분리.
       - 전체 소스 총계 115건 (Formal 69 + Official 12 + NON_EXP 28 + Reviewed 2 + Active Prospective 1 + Other 3) 완벽 보존.
    3. **Two-Parser Exact Reconciliation:**
       - 독립 1차 Raw Extractor와 2차 Production Parser 간 전수 1:1 대조 감사 (`MASTER_SOURCE_IDENTITY_AUDIT.json`, `.md`).
       - `RAW_COUNT == PARSED_COUNT == 28`, 제목 치환 0건, 지문 불일치 0건, 누락 0건, 위조 0건 전수 검증 통과 (`PASS_MASTER_SOURCE_IDENTITY`).
    4. **Fail-Closed 하드 가드 장착:**
       - `ResearchDiscoveryAgent` 0번 게이트에 Master Source Identity Gate 장착. 불일치 발견 시 즉각 `BLOCKED_MASTER_SOURCE_IDENTITY` 발동 및 아이디어 생성 원천 차단.
    5. **기존 Lineage Fix 및 후보 A/B/C 판정 보존:**
       - PAIR 20~22, CROWD 23~26 (`EXP-CROWD-20260823-005~008-V1`), PRIZE 27 다중 계보 등 이전 계보 수정 완전 보존.
       - 후보 C (IDEA-1243-CROS-003): 무관한 쌍둥이 회차 유입 차단 유지, PAIR repair 감사행 기준 `NEEDS_EVIDENCE` 유지 (자동 승격 0).
       - 후보 A/B: `REJECT_RESCUE` 유지.
  - **테스트 및 검증:**
    - 26개 신규 테스트 추가 (`TestMasterSourceIdentityAndFingerprint`), 총 136개 단위 테스트 전수 통과 (0 failures, 0 errors).
    - 공식 엔진 보호 검증: 변경 0건, Future Leakage 0건.
    - Git 반영: `P45 lock Research Master source identity`.
    - Vercel 배포: `VERCEL_DEPLOY_NOT_REQUIRED`.
    - 최종 판정: `PASS_MASTER_SOURCE_IDENTITY`.

- **2026-10-01: [CANONICAL RESEARCH DISPLAY & HYPOTHESIS IDENTITY LOCK FINALIZATION]**
  - **작업 목적:** 연구 디스커버리 표시/보고/증거 생성층에서 발생할 수 있는 정식 연구명 임의 치환(예: `EXP-DRAW-20260816-015-V1` "결손 회복속도" -> "전멸 회차속도", `EXP-DRAW-20260816-017-V1` "가변 전멸구간" -> "전멸 회귀선", `EXP-DRAW-20260816-026-V1` "숫자 간격 구조" -> "대척 동반 출현") 및 후보 가설 요약문 덮어쓰기 현상을 원천 차단하고, 7대 식별자 계층을 엄격히 분리하여 1:1 불변의 exact identity를 기계적으로 잠금.
  - **식별된 근본 원인 (Root Cause):**
    - 보고서 렌더러/직렬화기가 시맨틱 매칭 해석문(Semantic Interpretation/Summary)을 정식 등록 연구명(Canonical Title) 및 원문 가설(Original Hypothesis) 위치에 치환하여 출력하는 표시 계층 혼선 확인.
  - **핵심 구현 및 구조적 성과:**
    1. **7대 식별자 필드 계층 엄격 분리 (`canonical_display_resolver.py`):**
       - A. `canonical_title`: 정식 레지스트리(06_INITIAL_EXPERIMENT_REGISTRY.md)의 authoritative title. 불변.
       - B. `raw_title`: Master Section C / Source artifact 원문 title. 불변.
       - C. `candidate_name`: 후보 최초 생성 artifact의 원래 이름. 불변.
       - D. `hypothesis`: 최초 candidate artifact에 저장된 원문 가설. 요약문 덮어쓰기 절대 금지.
       - E. `opposite_hypothesis`: 원본 대립 가설 그대로 보존.
       - F. `semantic_title`: 검색/매칭 보조 표현 (변형 가능).
       - G. `display_summary`: 사람이 읽기 쉬운 설명문 (변형 가능).
       - 불변 제약: `semantic_title`과 `display_summary`는 절대 `canonical_title`, `raw_title`, `candidate_name`, `hypothesis`, `opposite_hypothesis`를 덮어쓰지 못함.
    2. **출처 지문 (Fingerprint) 잠금 및 Fail-Closed 감사 체계:**
       - 후보 고유 지문: `SHA256(candidate_id + candidate_name + hypothesis + opposite_hypothesis + discovery_data_end_round)`.
       - 정식 연구명 지문: `SHA256(canonical_registry_id + domain + canonical_title + version)`.
       - 표시 보고서 전수 감사: `CANONICAL_TITLE_SUBSTITUTION`, `CANDIDATE_NAME_SUBSTITUTION`, `HYPOTHESIS_SUBSTITUTION`, `OPPOSITE_HYPOTHESIS_SUBSTITUTION`, `DISPLAY_SOURCE_MISMATCH`, `CANDIDATE_IDENTITY_FINGERPRINT_MISMATCH` 모두 0건 검증 필수 (`PASS_CANONICAL_DISPLAY_IDENTITY`). 1건이라도 위반 시 `BLOCKED_DISPLAY_IDENTITY_INTEGRITY` 및 `READY_FOR_PROTOCOL = 0` Fail-Closed.
    3. **보고서 직렬화기 및 시맨틱 매처 정밀화 (`semantic_novelty_checker.py`):**
       - 시맨틱 매처는 유사도 점수와 사유(`semantic_reason`)만 별도 생성.
       - 정식 연구명은 레지스트리 row lookup의 `canonical_title_exact`만 출력.
       - 증거물 생성: `CANDIDATE_NOVELTY_EVIDENCE.json`, `.md` 및 `GOLDEN_CANDIDATE_DISPLAY_REPORT.json`, `.md` 동시 산출.
    4. **후보군 A/B/C 정밀 출력 검증:**
       - 후보 A (`IDEA-1243-NEGA-001`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260816-015-V1` = 결손 회복속도, `EXP-DRAW-20260816-017-V1` = 가변 전멸구간 (EXP-004)) 정확 출력, `REJECT_RESCUE` 유지.
       - 후보 B (`IDEA-1243-OPPO-002`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260816-026-V1` = 숫자 간격 구조 (EXP-008)) 정확 출력, `REJECT_RESCUE` 유지.
       - 후보 C (`IDEA-1243-CROS-003`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260824-010-V1` = OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT) 정확 출력, 쌍둥이 회차 오염 0건 유지, `NEEDS_EVIDENCE` 유지 (자동 승격 0).
  - **테스트 및 검증:**
    - 22개 신규 테스트 추가 (`tests_v27/test_canonical_display_identity.py`).
    - 총 158개 단위 테스트 전수 통과 (0 failures, 0 errors).
    - 공식 엔진 보호 검증: 변경 0건, Future Leakage 0건.
    - 로컬 런타임 활성화: `CANONICAL_DISPLAY_IDENTITY_GUARD_ACTIVE = YES`, `CANDIDATE_IDENTITY_LOCK_ACTIVE = YES`.
    - Git 반영: `P45 lock canonical research display identity`.
    - Vercel 배포: `VERCEL_DEPLOY_NOT_REQUIRED`.
    - 최종 판정: `PASS_CANONICAL_DISPLAY_IDENTITY`.

- **2026-10-01: [PAIR DORMANCY MEMORYLESS HAZARD V1 — CANDIDATE C FORMALIZATION & HISTORICAL SCREEN]**
  - **작업 목적:** 후보 C (`IDEA-1243-CROS-003`: `Pair Lifecycle Dormancy Duration Geometric Memory Invariance`)를 정식 Experiment Lab 연구로 승격하여 Protocol Lock, Calculator 구현, Preflight, Historical Backtest, 5-block Stability, Reproducibility, Prospective 준비 완결.
  - **정식 Experiment ID 발급:** `EXP-DRAW-20261001-001-V1` (Row 70).
  - **Human EXP Label:** `NONE` / `UNASSIGNED` (임의 EXP-021 부여 금지 준수).
  - **가설 보존:** 원문 Candidate 가설/대립가설 원본 그대로 불변 보존.
  - **통계적 설계 및 프로토콜 락:**
    - MAIN6 unordered pair C(45, 2) = 990, draw당 C(6, 2) = 15. BONUS 전면 제외.
    - 이론 기준: fair-draw pair analytic probability $p_0 = 1/66$.
    - Fixed Bins: Geometric quantiles $B_1=[1, 12], B_2=[13, 27], B_3=[28, 46], B_4=[47, 72], B_5=[73, 118], B_6=[119, \infty)$.
    - Primary Test Statistic: Global Likelihood-Ratio Deviance $T_{\text{global}}$ (Single primary endpoint; 990 pairwise inference 금지).
    - Primary Null: Round-order permutation null ($B = 4999$, deterministic seed `2359884131`).
    - Protocol SHA-256: `7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a`.
  - **Preflight 검증:** A~M 13개 전 항목 100% PASS.
  - **Historical Screen 결과 (1..1243):**
    - $T_{\text{global}} = 4.627019$, Permutation $p = 0.622400$ ($3111/4999 \ge T_{\text{obs}}$).
    - 최종 판정: **`FAILED_RETROSPECTIVE_SCREEN`**.
    - 엄격 해석: PAIR dormancy에 따른 temporal hazard effect를 검출할 근거가 없음 (p > 0.05). H0 비기각을 memorylessness의 수학적 증명으로 과장하지 않음.
    - 재현성: 독립 2회 실행 bitwise 완전 일치 (`PASS`).
    - Prospective 상태: Historical screen FAILED로 인해 자동 활성화 금지 -> `PROSPECTIVE_LOCK.json` 미생성, `PROSPECTIVE_STATE.json`에 비활성 기록.
  - **공식 엔진 보호:**
    - Official DB, Gates, Thresholds, Signatures, 1244 Sealed Predraw, Recommendations 100% FROZEN.
    - Future Leakage = 0 (1243 이후 데이터 완전 차단).
  - **테스트 및 검증:**
    - 32개 신규 테스트 추가 (`tests_v27/test_pair_dormancy_memoryless_v1.py`).
    - 총 190개 테스트 전수 통과 (0 failures, 0 errors).
    - 최종 판정: `PAIR_DORMANCY_V1_FAILED_RETROSPECTIVE`.




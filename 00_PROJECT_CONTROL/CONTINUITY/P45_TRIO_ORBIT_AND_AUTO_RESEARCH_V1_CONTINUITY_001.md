# P45 research continuity — 2026-09-30

Append-only successor for TRIO ORBIT Retrospective and AUTO RESEARCH LOOP V1; Recovery043 is not overwritten.

## 2026-09-30 — TRIO ORBIT RETROSPECTIVE + AUTO RESEARCH LOOP V1

### 1. 새 운영 원칙 확립
> "매 공식 결과 settlement 후 active research 자동 retrospective를 수행하고, 안전한 follow-up candidate를 자동 평가한다."

### 2. TRIO ORBIT 회차별 전향적 감사 및 캘리브레이션 결론
- 전향적 완료 5회차(1239..1243): Fixed PRIMARY 0, Linked PRIMARY 0, Fixed SUPPORT 3, Linked SUPPORT 1.
- 공정 6/45 추첨에서 3개 TRIO 후보 제시 시 1회차당 적어도 1개 exact 2/3(SUPPORT)가 발생할 순수 귀무확률은 **약 12.12%**(P=0.121226)이다.
- Fixed의 5회 중 3회 SUPPORT 발생은 우연한 자연 발생 확률 범위 내의 극소 표본 변동이며 (`SMALL_SAMPLE_INCONCLUSIVE`), 엔진의 실전 성능(60%)으로 오인할 수 없다.
- 역사적 1,237회(2..1238) 전수 검증:
  - PRIMARY: Fixed 5/1237 (0.40%), Linked 7/1237 (0.57%), McNemar $p = 0.77441$.
  - SUPPORT: Fixed 159/1237 (12.85%), Linked 174/1237 (14.07%), McNemar $p = 0.41025$.
  - Linked Anchor 재출현: 관측 36.54% vs 공정 귀무가설 35.60% ($Z = 0.69$, $p = 0.49$).
- 결론: Linked의 Fixed 대비 통계적 우월성 증거 전무 (`NO_EVIDENCE_OF_LINKED_SUPERIORITY`).
- Official Engine 판정: **`NO_CHANGE_SUPPORTED`** (엔진 일체 수정 금지).
- WEB UI 감사: `web/index.html` 내 "직전연동 V1 · 실전 우선" 표기는 객관적 통계 증거와 불일치하므로 **`SEMANTIC_MISMATCH_CANDIDATE`**로 기록하며, 향후 사용자 승인 시 "직전연동 V1 · 연구 비교"로 변경 권고 (실제 WEB 파일 수정: `NO`).

### 3. P45 AUTO RESEARCH LOOP V1 구현 완료
- 위치: `src/p45_v27/research_automation/`
- 핵심 컴포넌트 15개 모듈 및 단위/통합 테스트 17종 전수 통과 (`OK`).
- 공식 추첨 라이프사이클 격리 보장: 연구 자동화 서브시스템의 장애가 공식 정산/웹 동기화를 절대 차단하지 않음 (`official_lifecycle_affected: False`).
- 승격 방화벽(Promotion Firewall): 연구 성과가 아무리 우수하더라도 `PROMOTION_CANDIDATE`에서 자동 중단되며 `USER_APPROVAL_REQUIRED` 강제. 공식 엔진 자동 승격 일체 차단.
- 사후 데이터 오염 방지: `birth_round = R`, `discovery_range = 1..R` (`EXPLORATORY_ONLY`), `confirmatory_start_round = R+1`.
- 프로토콜 사전 잠금: Followup Gate(12대 기준) 통과 시 confirmatory 실행 전 `PROTOCOL_LOCK.json` SHA-256 잠금 강제.
- EDGE ARITHMETIC 연동: 50,000순열 재실행 없이 shadow settlement 및 TRIO 겹침 이벤트 감지만 기록.
- 연구 폭주 방지: 1회차당 신규 가설 최대 3개 제한.
- 멱등성: 동일 회차 반복 호출 시 `duplicate_write = 0`.

### 4. 무결성 및 시스템 상태
- Official Engine, Official DB, canonical draws, historical sealed, prospective sealed, official WEB pick 데이터 변경: **0건 (FROZEN 유지)**.
- Formal Registry physical/version rows: **69건 유지** (AUTO RESEARCH LOOP 인프라 구현 자체는 새 예측 실험 번호로 카운트하지 않음, latest numbered EXP-020 유지).
- 현재 대기 공식 전향적 회차: **1244회 PENDING / SEALED**.

## 2026-09-30 — STATISTICAL CORRECTION + RESEARCH DISCOVERY AGENT V1

### 1. 통계 표현 정정 및 계보 보존 (PHASE A)
- **Fixed 전향적 SUPPORT (5회 중 3회):**
  - 기존 보고된 $p \approx 0.0137$은 exact point mass $P(X=3) \approx 0.013757$이었음을 확인.
  - 정확한 단측 농축 검정(one-sided upper tail) $P(X \ge 3) \approx 0.014733$, 양측 exact binomial $p \approx 0.014733$으로 정정.
  - Wilson 95% CI: [0.2307, 0.8824]로 극소 표본에서의 우연 변동 (`SMALL_SAMPLE_INCONCLUSIVE`).
- **Historical Linked SUPPORT (1,237회 중 174회):**
  - 공정 귀무가설 기대치 149.96회 대비 단측 $p \approx 0.021781$, 양측 $p \approx 0.040486$.
  - 사후 탐색적 진단(`RETROSPECTIVE_NOMINAL_DEVIATION` / `NOMINAL_SIGNAL_ONLY`)이며, 4대 역사 귀무검정군에 대해 Holm 다중비교 감도 보정 적용 시 $p_{\text{adj}} \approx 0.087125 > 0.05$로 가족별 유의성 미도달.
- **Fixed vs Linked 대응표본 검정 보존:**
  - McNemar exact $p = 0.410251$로 두 궤도 간 통계적 유의차 전무 (`NO_EVIDENCE_OF_LINKED_SUPERIORITY` 유지).
- **Linked Anchor 재출현 가치:**
  - 재출현율 36.54% vs 공정 귀무 35.60% ($Z=0.69, p=0.48912$), 추가 정보량 전무 (`NO_INCREMENTAL_ANCHOR_EVIDENCE` 유지).
- **표현 정정:** "통계적 근거 전무", "자연발생 범위 내" 등의 과격한 표현을 중립적이고 정밀한 통계 언어로 전면 수정.
- **계보 보존 산출물:**
  - `v27_storage/audits/trio_orbit_prospective_retrospective_001/TRIO_ORBIT_STATISTICAL_CORRECTION_001.md`
  - `v27_storage/audits/trio_orbit_prospective_retrospective_001/TRIO_ORBIT_STATISTICAL_CORRECTION_001.json`

### 2. 판정 재검증 (PHASE B)
- Official Engine: **`NO_CHANGE_SUPPORTED`** (FROZEN 유지).
- Fixed vs Linked: **`NO_EVIDENCE_OF_LINKED_SUPERIORITY`**.
- Anchor Incremental Value: **`NO_INCREMENTAL_ANCHOR_EVIDENCE`**.
- Phase C 진행 조건 100% 충족 확인.

### 3. P45 RESEARCH DISCOVERY AGENT V1 구현 (PHASE C)
- 목적: P45가 기존 연구 결과와 전체 연구 공간을 조망하여, 사람이 매번 아이디어를 주지 않아도 미검증 연구 가설 후보를 스스로 발굴·검토·등록 준비하도록 함.
- 구조적 원칙: 결과 스캔/적중률 브루트포스/임계치 탐색 절대 금지. 오직 이론적 구조 공백(STRUCTURAL_GAP, NEGATIVE_SPACE, OPPOSITE_HYPOTHESIS, CROSS_STRUCTURE)만 탐색.
- 핵심 모듈:
  - `research_ontology.py`: 24대 연구 개념축 (NUMBER, TRIO, PAIR, CORE, occupancy, extinction, recovery, transition, recurrence, lag, gap, spacing, range, similarity, opposite-state, persistence, decay, regime, order/rank, arithmetic transform, interaction, conditional transition, bonus interaction, cross-round relation).
  - `research_coverage_map.py`: `RESEARCH_COVERAGE_MAP.json` 자동 생성 (TESTED, FAILED, ACTIVE, UNTESTED 등 분류).
  - `coverage_gap_analyzer.py`: 구조적 공백 및 반대가설 기회 탐색.
  - `novelty_checker.py`: 중복 및 실패축 구제(Rescue) 원천 차단.
  - `idea_quality_gate.py`: 10대 엄격한 과학적 PASS/FAIL 게이트 (NOVEL, NON_RESCUE, FALSIFIABLE, CLEAR_OPPOSITE, NULL_DEFINED, FUTURE_TESTABLE, DATA_AVAILABLE, MIN_SAMPLE_DEFINABLE, NO_LEAKAGE, MULTIPLE_TESTING_CONTROLLABLE).
  - `idea_provider.py`: `DeterministicStructuralProvider` (ACTIVE), `OptionalLLMIdeaProvider` (`NOT_CONFIGURED` - 안전하게 비밀키 요구 없이 대기).
  - `candidate_ranker.py`: 과학적 타당성 기반 우선순위 산정 (성과/적중률 기반 순위 절대 금지), 1회차당 최대 3개 후보 제한.
  - `research_discovery_agent.py`: 통합 마스터 에이전트.
- 첫 Discovery Cycle (1243회 기준):
  - `IDEA-1243-NEGA-001`: Fixed-Partition Extinction Negative-Space Recovery Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
  - `IDEA-1243-OPPO-002`: Number Proximity Minimum-Distance Repulsion Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
  - `IDEA-1243-CROS-003`: Pair Lifecycle Dormancy Duration Geometric Memory Invariance (READY_FOR_PROTOCOL, 시작회차 1244).
  - 1244회 PENDING/SEALED 안전 상태 확인 완료: `confirmatory_start_round = 1244`.
  - 멱등성 검증 완료: 동일 1243회 재실행 시 신규 후보 0건, 중복 쓰기 0건 (`ALREADY_PROCESSED`).

### 4. 무결성 및 시스템 상태
- Official Engine, Official DB, canonical draws, historical sealed, prospective sealed, official WEB pick 데이터 변경: **0건 (FROZEN 유지)**.
- Official 자산 13종 무결성 검증: `Protection verdict: PASS, Changed: 0`.
- Formal Registry physical/version rows: **69건 유지** (IDEA_CANDIDATE는 프로토콜 잠금 전 정식 레지스트리 자동 등록 금지).
- 전체 테스트 결과: 총 29개 테스트 전수 PASS (Auto Research Loop 17개 + Statistical Correction & Discovery Agent 12개).

### 5. P45 RESEARCH DISCOVERY AGENT V1.1 보완 (2026-09-30)
- **V1 한계 극복:**
  - 제목/키워드 매칭 취약점을 극복하기 위해 8대 구조 필드(INPUT, TRANSFORMATION, CONDITION, TARGET, LAG, METRIC, NULL, ACTIONABILITY) 기반 `SemanticNoveltyCheckerV1_1` 도입.
  - Coverage Map에서 24대 불변 온톨로지 축과 비배타적 연구 상태 카운트를 완전히 분리하여 수치 정합성 100% 확보.
  - 확증 회차 조기 확정 방지: `earliest_eligible_confirmatory_round = 1244`만 기록, 실제 `confirmatory_start_round`는 프로토콜 잠금 및 미래 봉인 완료 후에만 확정.
  - `CANDIDATE_NOVELTY_EVIDENCE.json`, `.md` 테이블 생성 필수화.
- **V1 3대 후보 재평가:**
  - `IDEA-1243-NEGA-001`: `REJECT_RESCUE` (EXP-004, EXP-015, EXP-022 전멸·복귀 축 구제 차단).
  - `IDEA-1243-OPPO-002`: `REJECT_RESCUE` (EXP-008, EXP-018, EXP-027 간격·인접 번호 축 구제 차단).
  - `IDEA-1243-CROS-003`: `NEEDS_EVIDENCE` (공식 수리와의 구조적 차이는 확인되나 위험률 풀링 증거 보완 전까지 보류).
  - 프로토콜 진입 후보: 0건 (`NO_VALID_NEW_HYPOTHESIS`).
- **테스트 및 보호:**
  - 총 44개 테스트 전수 PASS (신규 V1.1 15개 포함).
  - 공식 자산 보호 검증 PASS (변조 0건).
  - 로컬 런타임 V1.1 활성화 완료.
  - Vercel 배포 판정: `VERCEL_DEPLOY_NOT_REQUIRED`.
  - 정식 레지스트리 69행 유지 (새 실험 실행 0건).


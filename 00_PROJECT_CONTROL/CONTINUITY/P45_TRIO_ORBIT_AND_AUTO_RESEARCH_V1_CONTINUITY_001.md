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

### 6. P45 RESEARCH DISCOVERY AGENT V1.2 — KNOWLEDGE COVERAGE COMPLETION (2026-09-30)
- **배경 및 원인 분석:**
  - V1.1 보고 당시 Knowledge Index가 77건(Formal 69, Non-EXP 3, Official 5)으로 집계되었으나, authoritative Research Master에는 12 Official Internal 축 및 31 Non-EXP 실행 연구축이 실존함.
  - V1.1에서는 대표 축만 임의 추출하고 나머지를 누락하였던 구조적 공백이 발견됨.
  - "P45의 기존 연구 전체를 빠짐없이 읽고 있는가"를 증명하기 위해 전수 색인 체계 구축.
- **핵심 구현 및 성과:**
  - **Source Inventory (`RESEARCH_SOURCE_INVENTORY.*`):** 총 115건 수집 (Formal 69, Non-EXP 31, Official Internal 12, Reviewed Unexecuted 2, Active Prospective 1).
  - **Coverage Manifest (`RESEARCH_KNOWLEDGE_COVERAGE_MANIFEST.*`):** 115건 전수 매핑 (Mapped: 115/115 100.0%, Unmapped: 0건). DIRECT 107건, ALIAS 6건, MERGED 2건.
  - **Knowledge Index V1.2 (`RESEARCH_KNOWLEDGE_INDEX.*`):** 총 107건의 정규화 레코드 완성, 양방향 역추적 무결성 100% 검증. 미상 필드는 추측 배제하고 `UNKNOWN` 처리.
  - **Fail-Closed Mode:** `knowledge_coverage_complete != True` 시 신규 후보 생성 및 프로토콜 승격을 즉시 전면 차단 (`BLOCKED_KNOWLEDGE_COVERAGE_INCOMPLETE`).
  - **Coverage Map V1.2 연동:** 24대 불변 온톨로지 축과 107개 정규화 레코드 연동 완료 (고아 레코드 = 0건).
- **후보군 A/B/C 재검증:**
  - 후보 A (`IDEA-1243-NEGA-001`): `REJECT_RESCUE` 유지.
  - 후보 B (`IDEA-1243-OPPO-002`): `REJECT_RESCUE` 유지.
  - 후보 C (`IDEA-1243-CROS-003`): `NEEDS_EVIDENCE` 유지 (READY_FOR_PROTOCOL 자동 승격 금지, 새 실험 실행 0건).
- **무결성 및 검증 요약:**
  - 20대 신규 테스트 포함 총 64개 단위/통합 테스트 전수 통과 (0 failures, 0 errors).
  - Official 보호 검증 PASS: 엔진, DB, Sealed, Web pick 변경 0건. Future Leakage = 0.
  - 정식 레지스트리: 69행 유지 (새 실험 실행 0건).
  - 로컬 런타임 V1.2 Fail-Closed 가드 장착 및 활성화 확인.
  - Git Commit: `P45 complete research knowledge coverage guard` (main 브랜치 반영).
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.



### 7. P45 CANONICAL RESEARCH ID RESOLVER + REFERENTIAL INTEGRITY FINALIZATION (2026-09-30)
- **배경 및 원인 분석:**
  - V1.2에서 115개 원천 연구 항목의 전수 색인(100%)을 달성했으나, 인간 레이블(EXP-009)과 물리 레지스트리 행(EXP-DRAW-20260816-009-V1)의 숫자 서픽스 자동 동일시 위험이 발견됨.
  - EXP-DRAW-20260816-009-V1은 NUMBER RELATION LAB '전체 관계망' 연구이며, 공식 PAIR 라이프사이클 수리 감사 행은 EXP-DRAW-20260824-010-V1임.
  - 후보 A의 시맨틱 매칭에 무관한 EXP-DRAW-20260821-042-V1 (RETURN LAB 개별 숫자 return-age rank)이 유입되었던 문제 확인.
- **핵심 구현 및 성과:**
  - **식별자 네임스페이스 엄격 분리 (canonical_id_resolver.py):**
    - CANONICAL_REGISTRY_ID, HUMAN_EXP_LABEL, NON_EXP_ID, OFFICIAL_INTERNAL_ID, SOURCE_ITEM_ID 분리.
    - 서픽스 자동 매핑 엄격 차단 (EXP-009 != ...-009-V1).
    - 자동 생성 테이블: CANONICAL_REGISTRY_LOOKUP.json (69행), HUMAN_EXP_LABEL_MAP.json (28개 명시적 레이블).
  - **참조 무결성 전수 감사 (RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.*):**
    - 115개 원천 항목 전수 감사: 정식 레지스트리 참조 74건 전수 해결 (무효 0, 모호 0).
    - ALIAS 6건 전수 VALID, MERGED 2건 전수 VALID.
    - PAIR 수리 항목(SRC-NONEXP-20, 21, 22) 정규화 타깃을 EXP-DRAW-20260824-010-V1로 정정.
    - EXP-DRAW-20260816-009-V1 (전체 관계망) 및 EXP-DRAW-20260821-042-V1 (return-age rank) 보호 완료.
  - **Fail-Closed 참조 무결성 가드 및 시맨틱 매처 정밀화:**
    - 상위 매칭에 무효/모호 레지스트리 참조 유입 시 BLOCKED_REFERENTIAL_INTEGRITY로 차단.
    - 동일 도메인이 아닌 경우 실패 축 구제(FAILED_AXIS_RESCUE) 분류 금지 -> 후보 A에서 무관한 return-age 오매칭 원천 배제.
- **후보군 A/B/C 재평가:**
  - 후보 A (IDEA-1243-NEGA-001): REJECT_RESCUE 유지 (042 배제, EXP-004/015/022 기준 차단).
  - 후보 B (IDEA-1243-OPPO-002): REJECT_RESCUE 유지 (간격·반발 실패축 기준 차단).
  - 후보 C (IDEA-1243-CROS-003): NEEDS_EVIDENCE 유지 (READY_FOR_PROTOCOL 자동 승격 금지, 새 실험 실행 0건).
- **무결성 및 검증 요약:**
  - 22개 신규 테스트(	est_canonical_id_integrity.py) 포함 총 86개 테스트 전수 통과 (0 failures, 0 errors).
  - Official 보호 검증 PASS: 엔진, DB, Sealed, Web pick 변경 0건. Future Leakage = 0.
  - 정식 레지스트리: 69행 유지 (새 실험 실행 0건).
  - 로컬 런타임 활성화: CANONICAL_ID_RESOLVER_ACTIVE=YES, REFERENTIAL_INTEGRITY_GUARD_ACTIVE=YES.
  - Git Commit: P45 enforce canonical research ID integrity (main 브랜치 반영 예정).
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 web/* 수정 0건 -> VERCEL_DEPLOY_NOT_REQUIRED.



### 8. P45 NON-EXP 1:1 LINEAGE & SEMANTIC REFERENTIAL INTEGRITY FINAL PASS (2026-09-30)
- **배경 및 원인 분석:**
  - 기존 1차 참조 무결성 감사에서 `SRC-NONEXP-23` (Crowd topology 001)이 `EXP-DRAW-20260816-038-V2` (NO-PICK COVERAGE)에, `SRC-NONEXP-24` (Crowd topology 002)가 `EXP-DRAW-20260827-018-V2` (Residual Neighbor)에 각각 `VALID_ALIAS` 처리된 중대한 도메인/시맨틱 불일치 발견.
  - **테스트 결함 원인 (Root Cause):** 기존 감사 로직이 레지스트리 내 ID 존재 여부와 사유 문자열 내 키워드(`lineage`) 유무만 검사하고, 원천 도메인과 타깃 도메인 간 일치성(`source_domain == target_domain`) 및 명시적 파일 경로 증거를 검증하지 않는 단순 존재성 단언(existence-only assertion)에 머물렀기 때문임.
- **핵심 구현 및 전수 정정:**
  - **NON-EXP 31건 1:1 전수 계보 감사 체계 수립 (`NON_EXP_LINEAGE_AUDIT.json`, `NON_EXP_LINEAGE_AUDIT.md`):**
    - 31개 항목 전체에 대해 원천 도메인, 타깃 네임스페이스, 도메인 적합성, 온톨로지 적합성, 시맨틱 일치성, 명시적 계보 증거 경로를 1:1 대조.
    - 정식 레지스트리 부모가 없는 순수 독립 비실험 연구(23건: `SRC-NONEXP-01~19`, `28~31`)는 억지 별칭 부여 없이 `VALID_DIRECT`로 확정.
  - **핵심 계보 항목 정밀 정정:**
    - `SRC-NONEXP-23` (Crowd topology 001): 잘못된 DRAW 타깃을 취소하고, 레지스트리 58행 정식 물리 ID인 `EXP-CROWD-20260823-005-V1` (`EXP-CROWD-TOPO-001-V1`)에 `VALID_ALIAS` 연결 (증거: `EXP-CROWD-TOPO-001/supporting_audit_001/`).
    - `SRC-NONEXP-24` (Crowd topology 002): 잘못된 DRAW 타깃을 취소하고, 레지스트리 59행 정식 물리 ID인 `EXP-CROWD-20260823-006-V1` (`EXP-CROWD-TOPO-002-V1`)에 `VALID_ALIAS` 연결 (증거: `EXP-CROWD-TOPO-002/independent_reproduction_calibration/`).
    - `SRC-NONEXP-25` (Crowd topology 003): 60행 정식 물리 ID `EXP-CROWD-20260823-007-V1` (`EXP-CROWD-TOPO-003-V1`)에 `VALID_ALIAS` 연결.
    - `SRC-NONEXP-26` (Crowd retail 001): 61행 정식 물리 ID `EXP-CROWD-20260823-008-V1` (`EXP-CROWD-RETAIL-001-V1`)에 `VALID_ALIAS` 연결.
    - `SRC-NONEXP-27` (Prize-share 001/002): 단일 강제 alias 대신 `multi-target lineage`(`EXP-PRIZE-20260816-001-V2`, `EXP-PRIZE-20260821-004-V1`, `EXP-PRIZE-20260821-005-V1`)를 지원하는 `VALID_RELATED_DISTINCT`로 정립.
    - `SRC-NONEXP-20, 21, 22` (PAIR change-control 수리 계보): `EXP-DRAW-20260824-010-V1`과의 실질적 계보 증명(`VALID_ALIAS` 1건, `VALID_MERGE` 2건) 유지.
  - **도메인 호환성 하드 가드 (Domain Compatibility Hard Guard) 및 Fail-Closed 강화:**
    - CROWD -> DRAW, PRIZE -> DRAW, PAIR -> NUMBER RELATION 등 명시적 교차 증거 없는 오매칭 발생 시 `BLOCKED_NON_EXP_REFERENTIAL_INTEGRITY`로 즉각 차단.
    - `invalid_non_exp_lineage`, `ambiguous_non_exp_lineage`, `domain_mismatch_unjustified`, `alias_without_evidence`, `merge_without_lineage` 항목을 0으로 강제.
  - **후보 C 시맨틱 매처 무관 항목 배제:**
    - 한국어 서브스트링("쌍") 오인식으로 유입된 SIMILAR ROUND LAB의 '쌍둥이 회차 전이'(`EXP-DRAW-20260816-023-V1`, `024-V1`) 및 번호 순서 간격 연구를 상위 매칭에서 원천 배제.
    - 실질적 쌍 구조(`EXP-DRAW-20260824-010-V1`, `OFFICIAL-PAIR-LIFECYCLE`, `OFFICIAL-CORE-INVARIANTS`, `NON-EXP-03`) 중심으로 상위 근거 재구성.
    - 후보 C 최종 판정: `NEEDS_EVIDENCE` 유지 (자동 승격 0건, READY_FOR_PROTOCOL=0).
- **무결성 및 검증 요약:**
  - 신규 24개 테스트 포함 총 110개 테스트 전수 통과 (0 failures, 0 errors).
  - 정식 레지스트리 69행 유지 (신규 실험 0건, 신규 등록 0건).
  - Official 엔진, DB, Sealed, Web pick 변경 0건. Future Leakage = 0.
  - 최종 무결성 판정: `PASS_NON_EXP_REFERENTIAL_INTEGRITY` 복구 완료.
  - Git Commit: `P45 enforce non-EXP lineage integrity`.
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.

### 9. P45 MASTER SOURCE IDENTITY LOCK & INVENTORY FINGERPRINT FINAL AUDIT (2026-09-30)
- **배경 및 원인 분석 (Root Cause):**
  - 직전 보고에서 NON-EXP 항목명으로 "Number order statistical distribution", "Consecutive number adjacency structure" 등 실제 Research Master Section C에 존재하지 않는 합성 영문 연구명이 주입되는 치환 결함(Title Substitution) 확인.
  - Section C의 실제 연구 목록은 28개 축이며, 이후 추가된 3건의 실동 감사(Whole Engine, Trio Orbit 회고, Trio Orbit 통계교정)가 Section C에 혼입되어 31개로 하드코딩되었던 출처 분류 혼선 확인.
- **핵심 구현 및 불변 잠금 (Identity Lock):**
  - **독립 1차 원문 추출기 (`MasterSourceRawExtractor`):**
    - 기존 인벤토리/지식 빌더 모듈과 일체의 함수/변수를 공유하지 않는 독립 Raw Parser 구축.
    - Section C의 28개 한국어 원문 제목/텍스트를 번역·요약·치환 없이 1:1 보존한 `MASTER_NON_EXP_RAW_SNAPSHOT.json` 및 `.md` 생성.
    - 항목별 SHA-256 fingerprint 및 전체 섹션 SHA-256 fingerprint (`66baf18efd12f9ad6d1a6e9f5e80422a5cfe9539025937b5a7e77bbc39a2b6bf`) 산출 및 `MASTER_NON_EXP_SOURCE_FINGERPRINTS.json` 영구 보존.
  - **출처 분류 체계 분리:**
    - Section C 28개 축: `NON_EXP_EXECUTED` (28건)로 1:1 고정.
    - 이후 3건의 실동 감사: `SourceClass.OTHER_RESEARCH_SOURCE` (3건: `SRC-OTHER-01` ~ `SRC-OTHER-03`)로 정당 분리.
    - 전체 소스 총계 115건 (Formal 69 + Official 12 + NON_EXP 28 + Reviewed 2 + Active Prospective 1 + Other 3) 완벽 보존.
  - **Two-Parser Exact Reconciliation:**
    - 독립 1차 Raw Extractor와 2차 Production Parser 간 전수 1:1 대조 감사 (`MASTER_SOURCE_IDENTITY_AUDIT.json`, `.md`).
    - `RAW_COUNT == PARSED_COUNT == 28`, 제목 치환 0건, 지문 불일치 0건, 누락 0건, 위조 0건 전수 검증 통과 (`PASS_MASTER_SOURCE_IDENTITY`).
  - **Fail-Closed 하드 가드 장착:**
    - `ResearchDiscoveryAgent` 0번 게이트에 Master Source Identity Gate 장착. 불일치 발견 시 즉각 `BLOCKED_MASTER_SOURCE_IDENTITY` 발동 및 아이디어 생성 원천 차단.
  - **기존 Lineage Fix 및 후보 A/B/C 판정 보존:**
    - PAIR 20~22, CROWD 23~26 (`EXP-CROWD-20260823-005~008-V1`), PRIZE 27 다중 계보 등 이전 계보 수정 완전 보존.
    - 후보 C (IDEA-1243-CROS-003): 무관한 쌍둥이 회차 유입 차단 유지, PAIR repair 감사행 기준 `NEEDS_EVIDENCE` 유지 (자동 승격 0).
    - 후보 A/B: `REJECT_RESCUE` 유지.
- **무결성 및 검증 요약:**
  - 26개 신규 테스트 추가 (`TestMasterSourceIdentityAndFingerprint`), 총 136개 단위 테스트 전수 통과 (0 failures, 0 errors).
  - Official 엔진 보호 검증 PASS: 변경 0건, Future Leakage 0건.
  - 정식 레지스트리 69행 유지 (신규 실험 0건, 신규 등록 0건).
  - 로컬 런타임 활성화: MASTER_SOURCE_IDENTITY_GUARD_ACTIVE = YES.
  - 최종 무결성 판정: `PASS_MASTER_SOURCE_IDENTITY`.
  - Git Commit: `P45 lock Research Master source identity`.
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.

### 10. P45 CANONICAL RESEARCH DISPLAY & HYPOTHESIS IDENTITY LOCK (2026-10-01)
- **배경 및 원인 분석 (Root Cause):**
  - 연구 디스커버리 표시/보고/증거 생성층에서 정식 연구 식별자와 렌더링 명칭이 분리되지 않고, 시맨틱 매칭 해석 표현(예: "전멸 회차속도", "전멸 회귀선", "대척 동반 출현")이 레지스트리의 권위 있는 연구명(Canonical Title)을 덮어쓰는 표시 계층 결함 확인.
  - 후보 A/B/C의 가설 설명 또한 최초 생성 artifact 원문이 아닌 후속 시맨틱 요약문으로 대체될 위험 차단 필요.
- **핵심 구현 및 불변 잠금 (Identity Lock):**
  - **7대 식별자 계층 분리 (`CanonicalDisplayResolver`):**
    - `canonical_title`: Formal Registry authoritative title (변형 불가).
    - `raw_title`: Master Section C / Source artifact 원문 title (변형 불가).
    - `candidate_name`: 최초 생성 artifact 이름 (변형 불가).
    - `hypothesis`: 최초 candidate artifact 원문 가설 (요약 덮어쓰기 금지).
    - `opposite_hypothesis`: 원본 대립 가설 그대로 보존.
    - `semantic_title`: 보조 매칭 라벨 (변형 허용).
    - `display_summary`: 사람이 읽기 쉬운 설명 (변형 허용).
    - 불변 규칙: `semantic_title`과 `display_summary`는 권위 있는 제목/가설 필드를 절대 덮어쓰지 못함.
  - **출처 지문 (Fingerprint) 잠금 및 Fail-Closed 감사 체계:**
    - 후보 지문: `SHA256(candidate_id + candidate_name + hypothesis + opposite_hypothesis + discovery_data_end_round)`.
    - 정식 연구명 지문: `SHA256(canonical_registry_id + domain + canonical_title + version)`.
    - 보고서 전수 감사: `CANONICAL_TITLE_SUBSTITUTION`, `CANDIDATE_NAME_SUBSTITUTION`, `HYPOTHESIS_SUBSTITUTION`, `OPPOSITE_HYPOTHESIS_SUBSTITUTION`, `DISPLAY_SOURCE_MISMATCH`, `CANDIDATE_IDENTITY_FINGERPRINT_MISMATCH` 모두 0건 검증 필수. 위반 시 즉시 `BLOCKED_DISPLAY_IDENTITY_INTEGRITY` 및 `READY_FOR_PROTOCOL = 0`.
  - **보고서 직렬화기 및 시맨틱 매처 정밀화 (`SemanticNoveltyCheckerV1_1`):**
    - 시맨틱 매처는 유사도 점수와 사유(`semantic_reason`)만 별도 생성.
    - 정식 연구명은 레지스트리 row lookup의 `canonical_title_exact`만 출력.
    - 증거물 생성: `CANDIDATE_NOVELTY_EVIDENCE.json`, `.md` 및 `GOLDEN_CANDIDATE_DISPLAY_REPORT.json`, `.md` 동시 산출.
  - **후보군 A/B/C 정밀 출력 검증:**
    - 후보 A (`IDEA-1243-NEGA-001`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260816-015-V1` = 결손 회복속도, `EXP-DRAW-20260816-017-V1` = 가변 전멸구간 (EXP-004)) 정확 출력, `REJECT_RESCUE` 유지.
    - 후보 B (`IDEA-1243-OPPO-002`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260816-026-V1` = 숫자 간격 구조 (EXP-008)) 정확 출력, `REJECT_RESCUE` 유지.
    - 후보 C (`IDEA-1243-CROS-003`): 원문 가설 및 정식 연구명(`EXP-DRAW-20260824-010-V1` = OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT) 정확 출력, 쌍둥이 회차 오염 0건 유지, `NEEDS_EVIDENCE` 유지 (자동 승격 0).
- **무결성 및 검증 요약:**
  - 22개 신규 테스트 추가 (`TestCanonicalDisplayIdentity`), 총 158개 단위 테스트 전수 통과 (0 failures, 0 errors).
  - 공식 엔진 보호 검증 PASS: 변경 0건, Future Leakage 0건.
  - 정식 레지스트리 69행 유지 (신규 실험 0건, 신규 등록 0건).
  - 로컬 런타임 활성화: `CANONICAL_DISPLAY_IDENTITY_GUARD_ACTIVE = YES`, `CANDIDATE_IDENTITY_LOCK_ACTIVE = YES`.
  - 최종 무결성 판정: `PASS_CANONICAL_DISPLAY_IDENTITY`.
  - Git Commit: `P45 lock canonical research display identity`.
  - Vercel 배포 판정: 연구 백엔드 내부 변경으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.

### 11. P45 PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1 (EXP-DRAW-20261001-001-V1) FORMALIZATION & HISTORICAL SCREEN (2026-10-01)
- **배경 및 작업 목적:**
  - 사용자 승인에 따라 Candidate C (`IDEA-1243-CROS-003`: `Pair Lifecycle Dormancy Duration Geometric Memory Invariance`)를 정식 Experiment Lab 연구로 승격하여 프로토콜 설계, 락, 계산기 구현, 사전검증(Preflight), 과거검증(Historical Screen), 안정성 진단, 재현성 검증 및 prospective 준비 완결.
- **핵심 통제 원칙 및 규정:**
  - 공식 엔진(Official Engine) 완전 동결(FROZEN): 게이트, 임계치, 서명, DB, 1244 sealed predraw, 번호 추천 일체 변경 없음.
  - 임의 인간 약칭 `EXP-021` 부여 금지 준수: `human_exp_label = NONE (UNASSIGNED)`.
  - 정식 물리 ID: `EXP-DRAW-20261001-001-V1` (Authoritative Registry Row 70 발급).
  - 다중 검정(Multiple Testing) 통제: 단일 기본 평가변수($T_{\text{global}}$ LR deviance) 1개만 검정. 990개 pair별 개별 p-value 산출 금지.
  - 사후 편향 방지: 6개 기하분포 분위수 Bin 사전 고정 (`B1=1..12`, `B2=13..27`, `B3=28..46`, `B4=47..72`, `B5=73..118`, `B6=119+`), 사후 변경 금지.
  - Future Leakage 원천 차단: historical screen 데이터 상한 round 1243 강제 적용 (`Future Leakage = 0`).
- **Preflight 사전 검증 (13/13 PASS):**
  - A. C(45,2)=990 PASS
  - B. C(6,2)=15 PASS
  - C. 고정 pair 확률 $p_0 = 1/66$ exact PASS
  - D. Dormancy reset PASS
  - E. Age=1 정의 PASS
  - F. Left-censoring 제외 PASS
  - G. Bin 경계 Geometric quantiles 일치 PASS
  - H. Future data cutoff PASS
  - I. Deterministic seed 재현성 PASS (`seed = 2359884131`)
  - J. Permutation 불변량(draw 구성, 번호별 빈도, pair별 빈도) 보존 PASS
  - K. Permutation 시계열 순서 파괴 PASS
  - L. Protocol SHA-256 불변 검증 PASS (`7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a`)
  - M. Official 1244 sealed 파일 보호 PASS
- **과거 검증 (Historical Retrospective Screen) 결과:**
  - 분석 구간: 1회차 ~ 1243회차 (총 1,243개 draw, 1,162,896 risk exposures, 17,655 events).
  - Observed $T_{\text{global}} = 4.627019$.
  - Round-order Permutation Null ($B = 4999$, seed `2359884131`): $p_{\text{perm}} = 0.622400$ ($3,111 / 4,999 \ge T_{\text{obs}}$).
  - 최종 판정: **`FAILED_RETROSPECTIVE_SCREEN`**.
  - 결과 해석 준수: "이번 사전 고정 V1 global dormancy 검정에서는 PAIR dormancy에 따른 temporal hazard effect를 검출하지 못했다 (p = 0.6224 > 0.05)". H0 비기각은 memorylessness의 증명이 아니며, 사후 rescue/bin 변경 일체 금지.
  - 5구간 시간순 안정성 진단: Block 1 ($T=10.95$), Block 2 ($T=3.05$), Block 3 ($T=6.27$), Block 4 ($T=2.21$), Block 5 ($T=4.48$) - 보조 진단으로 주 판정 불변.
  - 재현성 검증: 동일 입력/시드로 독립 2회 실행 bitwise 완전 일치 (`PASS`).
  - Prospective 준비: 과거 선별 실패로 인해 자동 활성화 금지 -> `PROSPECTIVE_STATE.json`에 비활성 기록 (`PROSPECTIVE_LOCK.json` 미생성).
  - Discovery System 후보 C 상태: `FAILED` (lineage 보존, retired).
- **무결성 및 테스트 요약:**
  - 신규 32개 테스트 추가 (`tests_v27/test_pair_dormancy_memoryless_v1.py`).
  - 기존 158개 포함 총 190개 단위 테스트 전수 통과 (0 failures, 0 errors).
  - 정식 레지스트리: 70행 (EXP-DRAW-20261001-001-V1 등록 완료, Official Integration = false).
  - Official 엔진 보호 검증: 변경 0건, Future Leakage 0건.
  - Git Commit: `P45 formalize pair dormancy memoryless hazard V1`.
  - Vercel 배포 판정: 백엔드 연구 실험실 작업으로 `web/*` 수정 0건 -> `VERCEL_DEPLOY_NOT_REQUIRED`.
  - 최종 판정: `PAIR_DORMANCY_V1_FAILED_RETROSPECTIVE`.





## 2026-10-01 — TRIO ORBIT 1239~1243 sealed prospective failure decomposition

- Existing lineage `v27_storage/audits/trio_orbit_prospective_retrospective_001` CONTINUED; no new experiment, no Registry row, original scorecard/statistical correction preserved.
- All5sealed originals and settlements match canonical MAIN6+BONUS and prior SHA references, PASS. MAIN6-only scoring; pending1244 excluded.
- Fixed PRIMARY0/SUPPORT3; Linked PRIMARY0/SUPPORT1. Fixed coverage4/assembly1; Linked coverage5/assembly0. Total coverage9/assembly1/primary0.
- Root conclusion `PRIMARY_BOTTLENECK_NUMBER_POOL_COVERAGE`. One next direction `NUMBER / CANDIDATE-POOL SIGNAL`; descriptive priority only, no research automatically started.
- Fixed pool hits2/3/1/2/1, Linked2/1/2/1/2. Exact support and anchor mappings retained; no replacement numbers or new grouping rule.
- 1239 prior valid contiguous NUMBER-extinction evidence is directionally consistent but a distinct pool/rule; earlier defective snapshot remains invalid. No prior audit rerun.
- N5 cannot establish significance, Fixed/Linked superiority or persistent signal. EXP017 FAILED_NOT_SUPPORTED preserved; no consensus rescue.
- Official/DB/KTS45/WEB/1239..1244sealed changes0; number regeneration0, recommendations0, future leakage0. Protected SHA PASS; Registry byte-identical70.
- Evidence: `RESULT.md`, `RESULT.json`, `ROUND_TRACE.csv`, `INPUT_PROVENANCE.json`, `PROTECTED_HASH_REPORT.json`, `EVIDENCE_MANIFEST.json` in existing lineage. Important research decision retained.
- RESUME_FROM=COMPLETE for this decomposition; do not duplicate.

## 2026-10-05 — P45 WEB AUTO-LIFECYCLE FAILURE ROOT CAUSE REPAIR & 1244->1245 TRANSITION COMPLETE PASS

### 1. 장애 현상 및 최초 확인 (FAILURE CONFIRMED: YES)
- 1244회 공식 결과(2026-10-03 추첨: 1, 13, 18, 26, 34, 38 + 보너스 25) 발표 이후에도 WEB API(`https://p45project.vercel.app/api/status`) 및 로컬 WEB이 다음 1245회 출격으로 자동 전환되지 않고 1244회 PENDING / WAITING_FOR_RESULT 상태로 고착됨.
- 현장 상태 점검:
  - Canonical live 최신 회차: 1243 (1244 미반영)
  - 1244 settlement 부재
  - 1245 preview / seal 부재
  - 로컬 8045 포트 리스너 부재 및 `p45_v27.webapp` 프로세스 미실행 확인.

### 2. 최초 근본 원인 특정 (ROOT CAUSE: COORDINATOR_NOT_RUNNING + SCHEDULED_TASK_PATH_DEFECT)
1. **서버 상주 프로세스 부재 (`COORDINATOR_NOT_RUNNING`):**
   - 300초 주기 라이프사이클 총괄 코디네이터(`AutoUpdateCoordinator`)가 `p45_v27.webapp` 서버 데몬 내에만 존재하나, 서버 프로세스가 기동되어 있지 않았음.
2. **윈도우 작업 스케줄러 등록 경로 결함:**
   - 보조 자동화로 등록된 `\P45 Weekly Draw Update` 작업(토 22:30, 일 09:00 실행)이 `E:\P45 프로젝트\P45 회차 업데이트.cmd`를 호출하도록 되어 있었으나, 실제 파일은 `00_PROJECT_CONTROL\TOOLS\` 하위에만 존재하여 매 실행 시 종료 코드 1(`Last Result: 1`)로 실패함.
3. **스케줄러 작업 스코프 누락:**
   - 기존 `TOOLS\P45 회차 업데이트.cmd`는 `draw_update.py update`만 호출하여 번호 수집만 수행하고, 정산(`record_outcome`), 차기 생성/봉인(`preview_next`/`seal_next`), 웹 배포(`publish`)를 수행하지 않는 구조적 결함이 존재함.
4. **배포 단계 `-y` 플래그 누락 (`npx vercel`):**
   - `web_publish.py` 내 `npx.cmd vercel deploy --prod --yes` 호출 시 npx 자체에 `-y` 플래그가 없어 비대화형 환경에서 워커 타임아웃(EPIPE) 에러 발생 및 `VERCEL_DEPLOY_FAILED` 예외를 유발하는 잠재 결함 확인.

### 3. 수리 및 강화 내역 (REPAIR ACTIONS)
1. **`src/p45_v27/webapp.py`:**
   - `--once` CLI 옵션 추가: 웹 서버 데몬을 띄우지 않고도 단일 회차의 전체 라이프사이클(수집->정산->차기봉인->배포)을 즉시 결정론적으로 1회 완결 실행할 수 있도록 지원.
2. **`src/p45_v27/web_publish.py`:**
   - `cmd = ["npx.cmd" if os.name == "nt" else "npx", "-y", "vercel", "deploy", "--prod", "--yes"]`로 수정하여 비대화형 환경에서도 npx가 대화형 프롬프트나 패키지 워커 타임아웃 없이 무중단 배포되도록 수정.
3. **`00_PROJECT_CONTROL/TOOLS/P45 회차 업데이트.cmd`:**
   - 기존 단순 `draw_update` 호출을 `"%P45_PYTHON%" -m p45_v27.webapp --once`로 전면 교체하여 스케줄러 실행만으로도 전체 라이프사이클이 1회에 완결되도록 보장.
4. **루트 프록시 스크립트 신설 (`E:\P45 프로젝트\P45 회차 업데이트.cmd`):**
   - UTF-8 BOM 인코딩으로 루트에 배치하여 작업 스케줄러의 기존 등록 경로 및 직접 실행 모두 100% 정상 작동하도록 영구 보호.
5. **작업 스케줄러 재설치 및 실전 검증:**
   - `P45 자동업데이트 설치.ps1`을 재실행하여 정규 등록 완료, `schtasks /run` 수동 트리거 후 종료 코드 0(`Last Result: 0`) 확인.

### 4. 1244 정산 및 1245 전향적 봉인 완료
- **1244 공식 결과 반영:** 1, 13, 18, 26, 34, 38 (보너스 25), `SKIPPED_RESEARCH_HOLD`.
- **1244 봉인 원본 보존:** `e68ebccfce558798676466c664a17b325af72e5fb4ac1bf7a65dc1975d113b58` (변조 0건, 일치).
- **1244 적중 정산 결과:**
  - Fixed [9 11 25, 10 39 41, 12 14 28]: hits [0, 0, 0], PRIMARY 0, SUPPORT 0.
  - Linked [17 23 35, 5 32 38, 28 30 44]: hits [0, 1, 0] (38번 1수 일치), PRIMARY 0, SUPPORT 0.
  - 생성 파일: `P45_TRIO_ORBIT_TARGET_1244_OUTCOME_001.json`, `P45_TRIO_ORBIT_TARGET_1244_SETTLEMENT_001.json`, `STATE_012.json`.
- **1245 전향적 픽 생성 및 봉인:**
  - Fixed 3×3: `13 42 44`, `17 30 31`, `18 20 34`
  - Linked 3×3: `8 14 26`, `5 34 36`, `1 37 40` (기준번호 Anchors: 26, 34, 1)
  - 봉인 파일: `P45_TRIO_ORBIT_TARGET_1245_SEALED_PREDRAW_001.md`
  - 봉인 SHA-256: `dd40cb40bb6a6da0fff543008d693a0992045fc0b3c22b5f740e138c0e23a93d`
  - Future Leakage: 0, State: `STATE_013.json`.

### 5. WEB 동기화 및 재시작 내구성 검증
- **WEB 배포:**
  - `web_runtime/status.json` 갱신 및 Git main 브랜치 커밋/푸시(`c5969e1`).
  - Vercel 프로덕션 배포 완료 (`https://p45project.vercel.app/` 및 `https://p45.starm42.xyz/`).
  - 로컬, Vercel, 커스텀 도메인 3개 엔드포인트 100% 동일 데이터(1245회 PENDING) 일치 검증 PASS.
- **재시작 내구성 테스트 (A~F 전수 통과):**
  - 서버 완전 종료 후 재시작 시 startup 직후 lifecycle check 즉시 실행 확인 (`last_error: null`, `DRAW_ALREADY_CURRENT`, `WEB_ALREADY_CURRENT`).
  - 1245 봉인 SHA 불변 및 중복 쓰기 0건.
  - 300초 코디네이터 백그라운드 스레드 정상 상주 확인.
  - 브라우저 새로고침 및 API 재요청 후에도 1245회 완벽 유지.

### 6. 보호 검증 (PROTECTION VERDICT: PASS)
- Official Engine semantics: FROZEN 유지 (변경 0건).
- Official DB, canonical CSV/SQLite: 1244 1행 안전 추가 외 과거 데이터 변조 0건.
- 1244 봉인 원본 해시: `e68ebccf...` 100% 일치.
- Protected 5종 및 Official 3종 해시: 100% 일치 (변조 0건).
- Registry: 70행 일치.
- 최종 판정: **`PASS_AUTO_LIFECYCLE_REPAIRED_AND_1245_SEALED`**.


## 2026-10-05 — P45 AUTO-LIFECYCLE FINAL PRODUCTION HARDENING & CLOSEOUT

### 1. 개요 및 목적
- 매주 사람의 개입, 확인, 수동 테스트 없이 PC/웹서버 가용 상태에 따라 완전 자율적으로 라이프사이클(공식추첨수집 -> canonical update -> settlement -> next preview -> next seal -> web publish)이 완결되도록 운영 인프라 및 실패 복구 체계를 최종 마감(Closeout)함.

### 2. 기존 장애 원인 (Root Cause) 최종 상태
1. **서버 상주 의존 결함 (`COORDINATOR_NOT_RUNNING`):**
   - 상태: **RESOLVED**.
   - 내용: `webapp.py`에 `--once` CLI 옵션을 구현하여 웹서버 데몬 실행 여부와 무관하게 완전히 독립된 단일 프로세스로 풀 라이프사이클 실행 가능.
2. **스케줄러 경로 및 배치 디렉토리 해석 결함 (`SCHEDULED_TASK_PATH_DEFECT`):**
   - 상태: **RESOLVED**.
   - 내용: `00_PROJECT_CONTROL\TOOLS\P45 회차 업데이트.cmd`가 배치 스크립트 상위 2단계 디렉토리를 프로젝트 루트(`PROJECT_ROOT`)로 엄밀하게 역산(`for %%I in ("%~dp0..\..") do set "PROJECT_ROOT=%%~fI"`)하여 `PYTHONPATH` 설정 및 파이썬 종료 코드를 Task Scheduler에 그대로 반환(`exit /b %EXIT_CODE%`)하도록 수정. 루트 프록시 `P45 회차 업데이트.cmd`도 단일 위임 구조로 일원화.
3. **부분 작업 단독 실행 결함 (`PARTIAL_SCOPE_EXECUTION`):**
   - 상태: **RESOLVED**.
   - 내용: `draw_update` 단독 실행을 금지하고, 공식 결과 수집 -> 정산 -> 차기 봉인 -> 웹 배포까지의 Full lifecycle을 단일 실행(`webapp --once`)으로 통합.
4. **배포 환경 비대화형 대기 결함 (`DEPLOY_INTERACTIVE_HANG`):**
   - 상태: **RESOLVED**.
   - 내용: `web_publish.py`에 `-y` 플래그를 추가(`npx.cmd -y vercel deploy --prod --yes`)하여 비대화형 환경에서 대기/타임아웃 없이 무인 배포 완결.

### 3. 최종 Windows 작업 스케줄러 설정 (Task Scheduler Hardening)
- **대상 작업:** `\P45 Weekly Draw Update`
- **트리거 (Triggers):**
  1. 기본 트리거 (Primary): 매주 토요일 22:30 (`CalendarTrigger`)
  2. 보조 트리거 (Backup): 매주 일요일 09:00 (`CalendarTrigger`)
  3. 보완 캐치업 트리거 (Catch-up): 사용자 로그인 시 (`LogonTrigger -User sung2-PC\sung2`)
- **놓친 실행 복구 정책 (Missed-run Policy):**
  - `StartWhenAvailable = True` 활성화. 예정 시간에 PC가 꺼져 있었더라도 다음 부팅/가용 시 즉시 실행.
- **실패 자동 재시도 정책 (Failure Retry Policy):**
  - `RestartCount = 4`, `RestartInterval = PT15M` (15분 간격, 최대 4회 자동 재시도).
  - 배치 파일 및 `webapp.py`가 오류 발생 시 0이 아닌 종료 코드(`exit /b 1`)를 정확히 반환하여 스케줄러 재시도 메커니즘 정상 연동.
- **중복 병렬 실행 방지 (Duplicate Policy):**
  - `MultipleInstancesPolicy = IgnoreNew` (`DO_NOT_START_NEW`).
  - 근거: P45 라이프사이클은 1회 실행으로 최신 상태까지 일괄 반영하므로 병렬 큐잉보다 실행 중인 작업을 유지하고 신규 시작을 안전 무시하는 것이 파일 락 및 Git 충돌을 방지하는 최선의 정책임.
- **로그인/부팅 의존도 및 보안 제약:**
  - 사용자 계정 비밀번호를 저장하지 않는 Interactive 보안 모델을 유지하며, 무인 백그라운드 비밀번호 저장 대신 `AtLogOn -User sung2` + `StartWhenAvailable` 조합으로 로그인 시점 즉시 무인 캐치업 보완. (보안 제약: `SECURITY_BLOCKED_UNATTENDED_PASSWORD_STORAGE` 안전 수렴).
- **스케줄러 실측 결과:**
  - `schtasks /run` 실행 후 `Last Result: 0` 정상 확인.

### 4. 단일 권위 실행 진입점 (Authoritative Entrypoint)
- **공식 단일 실행 명령:**
  `"%P45_PYTHON%" -m p45_v27.webapp --once --trigger-source "%P45_TRIGGER_SOURCE%"`
- **공식 배치 경로:**
  - 내부: `E:\P45 프로젝트\00_PROJECT_CONTROL\TOOLS\P45 회차 업데이트.cmd`
  - 루트: `E:\P45 프로젝트\P45 회차 업데이트.cmd` (내부 경로로 100% 위임)

### 5. 실패 복구 및 내구성 로깅 (Failure Recovery & Durable Logging)
- **내구성 실행 로그:**
  - `v27_storage/live/p45_lifecycle_runs.jsonl`에 매 실행 시 영구 append:
    `timestamp`, `trigger_source`, `target`, `canonical_latest`, `steps`, `success`, `error`, `deploy_result`, `final_state`.
- **지연 상태 자동 캐치업 (Stale-State Safety):**
  - `canonical latest >= prospective target` 상태 감지 시 `while` 루프로 미완료된 과거 회차 순차 정산 후 차기 회차 단일 봉인 및 웹 배포까지 자동 연속 실행.
- **안전 Idempotency:**
  - 이미 최신 상태에서 실행 시 `["DRAW_ALREADY_CURRENT", "WEB_ALREADY_CURRENT"]`로 즉각 no-op 종료 (신규 쓰기 0건, 봉인 불변, 소요 시간 ~1초).

### 6. 무결성 및 보호 검증 (Protection Verdict)
- Official Engine semantics: FROZEN 유지 (변경 0건)
- Protocol Locked 파일 (5종): 100% SHA-256 일치 (변조 0건)
- Official Protected 파일 (3종): 100% SHA-256 일치 (변조 0건)
- 1244 봉인 원본 해시: `e68ebccfce558798676466c664a17b325af72e5fb4ac1bf7a65dc1975d113b58` (PASS)
- 1245 전향 봉인 해시: `dd40cb40bb6a6da0fff543008d693a0992045fc0b3c22b5f740e138c0e23a93d` (PASS)
- Registry 정식 물리 행: 70행 완전 보존 (DRAW 55 / CROWD 9 / PRIZE 6)
- Future Leakage: 0

### 7. 최종 클로즈아웃 판정
- **판정: `AUTO_LIFECYCLE_PRODUCTION_CLOSED`**
- **향후 매주 남은 수동 작업 (Remaining Manual Weekly Action): `NONE`**




---

## 2026-10-19 — P45 AUTO-LIFECYCLE CLOUD MIGRATION FINAL

> 과거 2026-10-05의 `AUTO_LIFECYCLE_PRODUCTION_CLOSED` 판단은 역사적 기록으로 보존하며, 이번 클라우드 완전 이전(Cloud Migration)이 이를 공식 Supersede한다.

### 1. 이번 장애 재발 일시 및 최초 원인 (Root Cause Analysis)
- **발생 일시:** 2026-10-17(토) 1246회 공식 추첨 이후 ~ 2026-10-19(월)
- **증상:** 프로덕션 Vercel 및 Custom Domain API가 1245회에 머물러 있는 Stale 상태 잔류 (`canonical: 1245, current: 1246 PENDING`).
- **최초 근본 원인 (Confirmed Root Cause):**
  1. `MISSED_TRIGGER`: Windows 작업 스케줄러 `P45 Weekly Draw Update`의 토요일 주 트리거가 22:30이 아닌 오전 10:30:00 AM으로 오등록되어 10/17(토) 추첨 발표 후 야간에 전혀 트리거되지 않음.
  2. `LOCAL_PC_NOT_AVAILABLE`: 주말 야간 및 일요일 PC 전원 오프라인으로 인해 일요일 백업 트리거(09:00)가 미실행됨.
  3. `VERCEL_DEPLOY_FAILED`: 10/19(월) 아침 사용자 로그인 시 LogonTrigger로 일부(데이터 수집/정산/봉인) 실행되었으나, Vercel Git Integration 부재 상태에서 로컬 Vercel CLI 배포 도중 프로세스 비정상 종료(0xC000013A, STATUS_CONTROL_C_EXIT)가 발생하여 Vercel 프로덕션에 미반영됨.
  4. `STATE_PERSISTENCE_LEAK`: 기존 `web_publish.py`가 오직 `web_runtime/status.json`만 스테이징하고 canonical CSV, SQLite, prospective 정산/봉인 자산을 Git 커밋에서 누락시켜 클라우드 러너 호환성 결여.

### 2. Local-PC 의존성 영구 폐기 및 클라우드 이전 결정
- **PRIMARY 자동화:** GitHub Actions scheduled workflow (`.github/workflows/p45-auto-lifecycle.yml`)
- **FALLBACK 자동화:** GitHub Actions `workflow_dispatch` 수동 원클릭 실행
- **LOCAL WINDOWS:** 비상용 수동 도구로만 유지 (`00_PROJECT_CONTROL/TOOLS/P45 회차 업데이트.cmd`), Windows 주간 스케줄러는 영구 비활성화(Disabled).

### 3. 클라우드 스케줄 및 동시성 설계
- **스케줄 (한국시간 KST 기준 / UTC 변환):**
  - 토요일 22:00 KST (`cron: '0 13 * * 6'`)
  - 토요일 22:30 KST (`cron: '30 13 * * 6'`)
  - 토요일 23:00 KST (`cron: '0 14 * * 6'`)
  - 토요일 23:30 KST (`cron: '30 14 * * 6'`)
  - 일요일 09:00 KST (`cron: '0 0 * * 0'`)
- **동시성 제어:**
  `concurrency: { group: p45-auto-lifecycle, cancel-in-progress: false }` 로 동일 라이프사이클의 병렬 실행 원천 차단.
- **최소 권한:** `permissions: { contents: write }`

### 4. 상태 영속성 (Authoritative State Persistence)
- `web_publish.py` 전면 리팩토링:
  다음 authoritative 핵심 자산을 단일 커밋으로 원자적 Git 동기화:
  - `web_runtime/status.json`
  - `v27_storage/live/p45_live_draws.csv`
  - `v27_storage/live/p45_new_draw_update_v1.sqlite3`
  - `v27_storage/live/p45_lifecycle_runs.jsonl`
  - `v27_storage/prospective/trio_orbit_v1_001` (전체 정산, 봉인 마크다운, 상태 파일)

### 5. 프로덕션 Vercel 배포 전략
- GitHub Actions 시크릿(`VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`) 최신 동기화 완료.
- `web_publish.py`에 Token-Aware Vercel CLI 배포 연동 및 프로덕션 엔드포인트 15회 Bounded Poll/Retry 검증 탑재.
- 이미 동기화된 상태에서는 `WEB_ALREADY_CURRENT`로 중복 배포 0건 보장.

### 6. 회차 복구 및 전향 봉인 결과
- **Canonical Latest:** 1246회 (2026-10-17: 16, 22, 23, 24, 27, 28 + 6)
- **Settlement Latest:** 1246회 정산 완료 (`P45_TRIO_ORBIT_TARGET_1246_SETTLEMENT_001.json`)
- **차기 봉인 회차:** 1247회 (`P45_TRIO_ORBIT_TARGET_1247_SEALED_PREDRAW_001.md`)
  - FIXED A: `1 12 29`
  - FIXED B: `2 34 45`
  - FIXED C: `3 7 20`
  - ANCHOR A/B/C: `28`, `6`, `22`
  - LINKED A: `28 29 36`
  - LINKED B: `6 43 44`
  - LINKED C: `22 23 45`
  - 봉인 SHA-256: `eb38a57cfee5cc6a804a52ef89c9629a8b0076585c3c40df60ecf84a2f1522f0`
- **배포 실측 반영:**
  - `https://p45project.vercel.app/api/status` -> 1246 완료 / 1247 PENDING (PASS)
  - `https://p45.starm42.xyz/api/status` -> 1246 완료 / 1247 PENDING (PASS)

### 7. 무결성 및 내결함성 테스트 (Fault-Injection Verdict)
- `tests/test_auto_publish_fault_injection.py`: 5개 시나리오(TEST A~E) 100% PASS.
- `tests/test_cloud_lifecycle_fault_injection.py`: 8개 시나리오(A~H) 100% PASS:
  - Clean runner --once execution PASS
  - Already-current 0 writes / 0 mutation PASS
  - Temporary fetch failure graceful retry PASS
  - Deployment delay bounded retry PASS
  - Git push no-change 0 empty commit PASS
  - Multiple simultaneous triggers concurrency block PASS
  - Existing seal immutability 100% PASS
  - Multi-round stale chronological catch-up PASS
- 과거 봉인 해시(1239..1246): 100% 불변 보존 PASS.
- Official Engine: FROZEN 유지, Future Leakage: 0.

### 8. Windows 스케줄러 퇴역 (Retirement)
- 작업명 `\P45 Weekly Draw Update`: `schtasks /change /tn "P45 Weekly Draw Update" /disable` 실행으로 영구 비활성화 확인 (`상태: 사용할 수 없음`).
- 수동 복구 배치 파일만 로컬에 보존.

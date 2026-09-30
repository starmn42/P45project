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


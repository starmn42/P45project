# EXP-003 워크포워드

각 R에서 `source_end_round=R-1`을 강제한다. R-1 MAIN으로 45개 번호의 거리와 구간 feature를 만들고 canonical prediction payload/hash를 먼저 전용 DB에 잠근다. 그 뒤에만 R MAIN/bonus를 읽어 거리별 outcome을 기록한다.

기간은 전체, 전반부, 후반부, 최근100, 최근50이며 최근20은 TEST_ONLY다. feature나 threshold는 중간성과로 변경하지 않는다.

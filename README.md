# P45 Research Engine

P45 v2.3 지침을 코드로 구현하는 프로젝트입니다.

## Phase 2 — 공식 당첨번호 가져오기

동행복권의 현재 공식 결과 페이지와 데이터 응답을 사용합니다. 원본 HTML과 JSON 응답을 그대로 보존하며, 전체 회차가 연속적으로 수집된 경우에만 CSV 묶음을 확정합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 fetch --output .\downloads
```

수집 결과의 상태는 `COLLECTED_UNVERIFIED`입니다. 페이즈 3 데이터 검사를 통과하기 전에는 분석 자료로 사용하지 않습니다. 같은 최신 회차의 수집 묶음이 이미 있으면 덮어쓰지 않습니다.

## Phase 3 — 데이터 검사

공식 분석 전에 반드시 거쳐야 하는 데이터 입력, 검사, 정규화와 해시 기록입니다.

페이즈 2 수집 묶음을 검사하고 분석용 데이터로 확정합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 validate --collection .\downloads\official-1-1235 --output .\validated
```

형님이 제공한 CSV와 공식 자료를 대조하려면 다음처럼 실행합니다. 날짜·본번호·보너스 또는 회차 범위가 하나라도 다르면 확정을 중단하고 `conflict-report.json`을 만듭니다.

```powershell
python -m p45 validate --collection .\downloads\official-1-1235 --user-csv .\data\draws.csv --output .\validated
```

## Phase 4 — 기본 구조 분석

페이즈 3에서 확정된 데이터만 사용해 보너스 포함 7개 구조와 기간별 통계를 생성합니다. 대상 회차가 생략되면 다음 회차를 분석하며, 과거 회차를 지정하면 해당 회차 직전까지만 별도 입력으로 고정합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 structure --dataset .\validated\validated-1-1235 --output .\analysis
```

과거 시점 구조를 만들 때:

```powershell
python -m p45 structure --dataset .\validated\validated-1-1235 --target-round 1000 --output .\analysis
```

이 단계는 후보나 임의 점수를 만들지 않습니다. 최근20 통계는 `OBSERVATION_ONLY`로 표시됩니다.

## Phase 5 — 과거 회차 시험

각 R회 시험 조건은 R-1회까지만 보고 만들고, R회 결과로 평가합니다. 전멸구간 하나를 사건 하나로 기록하며 복귀 깊이와 연속 전멸을 본번호·보너스 포함 기준으로 나눠 저장합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 backtest --structure .\analysis\structure-1236 --output .\backtests
```

후보가 아직 없는 단계이므로 후보 적중률 기반 공식 관문과 구조 붕괴 최종 단계는 `HOLD`입니다. 임의 기준값을 추가하지 않습니다.

## Phase 6 — 후보 판정

복귀구간 내부 번호와 비복귀 TEST 번호를 분리해 번호별 전체·전후반·최근100·50·20, 본번호·보너스·통합 성과와 공식 관문을 계산합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 candidates --structure .\analysis\structure-1236 --backtest .\backtests\backtest-1236 --output .\candidate-results
```

지침에 수치 기준이 없는 반대 가설 위험과 구조 붕괴 관문은 `UNRESOLVED`이며 후보를 임의로 PASS시키지 않습니다.

## Phase 7 — 최종 6개 선택

공식 PASS 후보를 우선 확인하고, 부족하면 공식 결과를 HOLD합니다. 공식 후보와 유효 비복귀 TEST 후보의 합도 6개 미만이면 MIXED_TEST 역시 HOLD하며 번호를 강제로 채우지 않습니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 select --candidates .\candidate-results\candidates-1236 --output .\selections
```

선택 결과가 정확히 6개일 때만 페이즈 8 세트 배치로 전달됩니다.

## Phase 8 — 두 세트 배치

최종 6개를 확정한 뒤에만 세트1과 세트2에 각각 3개씩 배치합니다. 복귀 후보를 먼저 분산하고 같은 역할·9단위 구간·독립근거 구성을 순서대로 분산합니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 place --selection .\selections\selection-1236 --candidates .\candidate-results\candidates-1236 --output .\sets
```

최종 후보가 6개가 아니면 번호를 채우지 않고 `HOLD` 보고서를 생성합니다.

## Phase 9 — 결과 저장과 복기

1~8단계 전체 결과를 불변 스냅샷으로 잠급니다. 동일 회차 기록은 다시 만들거나 덮어쓸 수 없습니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 lock --dataset .\validated\validated-1-1235 --structure .\analysis\structure-1236 --backtest .\backtests\backtest-1236 --candidates .\candidate-results\candidates-1236 --selection .\selections\selection-1236 --sets .\sets\sets-1236 --ledger .\ledger
```

실제 결과 발표 후에는 잠금 기록을 수정하지 않고 별도 복기를 추가합니다.

```powershell
python -m p45 review --ledger .\ledger --round 1236 --main 1 2 3 4 5 6 --bonus 7
```

## Phase 10 — 휴대폰 배포

PC와 휴대폰이 동일한 Python 엔진과 불변 장부를 사용하는 모바일 우선 PWA입니다.

PC에서 실행:

```powershell
$env:PYTHONPATH = "src"
python -m p45.webapp --host 0.0.0.0 --port 8045
```

같은 Wi-Fi의 휴대폰에서 PC의 내부 IP와 포트로 접속합니다. 예: `http://192.168.0.10:8045`. 외부 배포 및 홈 화면 설치에는 HTTPS 호스팅이 필요합니다. 서버를 인터넷에 직접 노출하지 말고, 정식 배포 시 HTTPS 역방향 프록시나 신뢰할 수 있는 호스팅을 사용하세요.

화면 기능:

- 10개 페이즈 진행 상태
- 현재 구조와 공식/MIXED_TEST 상태
- 새 공식 데이터 확인 및 전체 분석
- 잠금 기록 무결성 검사
- 실제 결과 복기 입력
- 모바일 홈 화면 설치 및 정적 화면 오프라인 캐시

입력 CSV 열은 다음과 같습니다.

```csv
round,date,n1,n2,n3,n4,n5,n6,bonus
1,2002-12-07,10,23,29,33,37,40,16
```

- `round`: 1부터 시작하는 연속 회차
- `date`: `YYYY-MM-DD` 형식 (선택 가능하나 열은 유지)
- `n1`~`n6`: 본번호 6개
- `bonus`: 보너스번호 1개

검증에 성공하면 원본 복사본, 정규화 CSV, `metadata.json`이 한 분석 묶음으로 저장됩니다. 오류가 하나라도 있으면 아무 분석 묶음도 확정하지 않습니다.

```powershell
python -m p45 prepare --input .\data\draws.csv --output .\artifacts --source "사용자 제공"
```

소스 체크아웃에서 실행할 때는 다음처럼 모듈 경로를 지정할 수 있습니다.

```powershell
$env:PYTHONPATH = "src"
python -m p45 prepare --input .\data\draws.csv --output .\artifacts --source "사용자 제공"
```

테스트:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

공식 사이트 자동 수집과 후보 분석은 Phase 1 범위에 포함하지 않습니다. 출처가 다른 데이터의 자동 병합도 하지 않으며, 비교 시 충돌을 보고하고 확정을 중단하는 것이 원칙입니다.

# P45 PROTECTION HASH CONSISTENCY AUDIT 017

## 판정

`REPORTING_SCOPE_DIFFERENCE`

2026-08-24 EXP-CROWD-RETAIL-001 독립재현/판매점성향 보정감사 완료 보고에서
`051a9add7b8bd68030a014c6f3d2e33226f4fc2db6e2cf90a0647f82349621dd`를
`PROTECTED_CANONICAL_HASH`라고 표시한 것은 라벨 오류다.

두 해시는 서로 다른 대상을 나타낸다.

- 공식 protected canonical content hash:
  `7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb`
- 위 값을 담고 있는 `v27_storage/manifests/protected-canonical-v1.json` 파일 자체의 SHA-256:
  `051a9add7b8bd68030a014c6f3d2e33226f4fc2db6e2cf90a0647f82349621dd`

## 공식 scope

공식 protected canonical hash는 다음 6개 root의 각 content manifest hash를 root 이름순 canonical JSON으로 직렬화한 뒤 SHA-256으로 계산한다.

- `src/p45`: 14 files
- `analysis`: 4 files
- `ledger`: 20 files
- `validated`: 3 files
- `experimental`: 11 files
- `ledger-experimental`: 20 files

총 보호 파일은 72개이며 `__pycache__`, `.pyc`, `.pyo`는 제외된다.

현재 파일을 동일 구현 `src/p45_v27/protection_manifest.py::build_manifest`로 다시 계산한 결과는
`7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb`이다.
기준 manifest와 file-by-file 비교 결과 변경 파일은 0개다.

## 연대기 증거

- Decision 088 snapshot manifest: canonical content hash `7c145...`
- Decision 089 snapshot manifest: canonical content hash `7c145...`
- Current State/Handoff 및 portable external source: canonical content hash `7c145...`
- manifest JSON 파일은 2026-08-07 이후 동일하며 파일 SHA는 `051a9...`

Decision 089 작업의 durable state snapshot은 작업 전후 canonical content hash를 모두 `7c145...`로 기록한다.
별도의 pre/post evidence 파일은 만들지 않았지만, 기준 manifest와 현재 72개 파일의 개별 SHA/크기가 전부 일치한다.

## 정정

앞으로 명칭을 다음처럼 고정한다.

- `PROTECTED_CANONICAL_CONTENT_HASH` = `7c145...`
- `PROTECTED_MANIFEST_FILE_SHA256` = `051a9...`

보호 파일 변경, 복구, 되돌리기, 연구 규칙 변경은 없었다. 연구는 계속할 수 있다.

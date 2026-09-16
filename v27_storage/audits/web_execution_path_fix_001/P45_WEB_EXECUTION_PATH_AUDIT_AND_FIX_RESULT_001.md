# P45 WEB EXECUTION PATH AUDIT + MINIMAL FIX RESULT 001

## Verdict

`PARTIAL_DEVICE_SIDE_NOT_CONFIRMED`

PC and LAN routes are repaired and verified. A physical phone was not available for device-side confirmation.

## Actual execution chains

### PC

`P45 시작.cmd` → project root `E:\P45 프로젝트` → bundled Python → `PYTHONPATH=E:\P45 프로젝트\src` → `python -m p45_v27.webapp --host 127.0.0.1 --port 8045` → `ExclusiveThreadingHTTPServer` → static `web/` + `FrozenWebAdapter` → `ProspectiveOrbitService` → browser `http://127.0.0.1:8045/` → frontend same-origin `GET /api/status`.

### Phone

`P45 휴대폰 미리보기.cmd` → bundled Python → `python -m p45_v27.lan_ip` → LAN IPv4 `172.30.1.20` → `python -m p45_v27.webapp --host 0.0.0.0 --port 8045` → PC browser `http://127.0.0.1:8045/` and displayed phone URL `http://172.30.1.20:8045/` → same static/API server.

There is no separate frontend server. `/app.js?v=40` calls relative `/api/status`, so frontend and backend use the same origin and project copy. No active path references the removed P45 HOME.

## Root causes

1. `START_SCRIPT_PATH_ERROR / COMMAND_QUOTING_ERROR`
   - The phone launcher's `FOR /F` backquoted inline-Python command was reparsed by CMD.
   - Before change it emitted an invalid command beginning with the Python path and stopped before server startup.
   - Moving LAN detection to `p45_v27.lan_ip` removes nested command, quote, and parenthesis parsing from the launcher.
2. `WEB_PROJECTION_DUPLICATE`
   - The append-only prospective ledger legitimately contains pre-outcome and settlement versions for target 1239.
   - `rows_for_display` replaced every matching source row with the same effective settled row, displaying and counting 1239 twice.
   - The read projection now keeps the latest row per target and substitutes the verified effective row once. The source ledger is untouched.

## Not confirmed as causes

- port conflict before test: `NOT_CONFIRMED`; port 8045 was initially free.
- wrong working directory/project copy/P45 HOME reference: `NOT_CONFIRMED`; active chain consistently resolves `E:\P45 프로젝트`.
- API base mismatch: `NOT_CONFIRMED`; frontend uses same-origin `/api/status`.
- stale static asset: `NOT_CONFIRMED`; server sends `no-store`, assets use versioned URLs, and no service-worker registration is active in `app.js`.

## Modified files

- `P45 휴대폰 미리보기.cmd`: replace fragile inline Python with `python -m p45_v27.lan_ip`.
- `src/p45_v27/prospective_web.py`: collapse append-only target versions only in the read projection.

## Added files

- `src/p45_v27/lan_ip.py`: read-only LAN IPv4 detector.
- `tests/test_web_execution_path_fix_001.py`: launcher/projection/non-loopback regression tests.

## Verification

- PC launcher exit: `0`
- PC listener: `127.0.0.1:8045`
- PC home/API: `200 / 200`
- browser title: `P45 TRIO ORBIT · Prospective Web V1`
- browser target/canonical: `1239 / 1239`
- browser prospective rows/completed: `1 / 1`
- browser console warnings/errors: `0`
- phone launcher LAN URL: `http://172.30.1.20:8045/`
- phone listener: `0.0.0.0:8045`
- LAN home/API from PC: `200 / 200`
- LAN API prospective rows/completed: `1 / 1`
- regression tests: `3/3 PASS`
- physical phone: `NOT_CONFIRMED`

## Documentation discrepancy observed, not changed

`P45_NEW_CHAT_START_HERE_003.md` still points to Recovery 036, Master 002, and Evidence Inventory 001. Recovery 038 is authoritative and points to the current versions. This discrepancy does not participate in the active web execution chain, so it was recorded rather than changed.

## Protection

- canonical draw: `1..1239`, missing `0`, duplicate `0`, CSV/SQLite equality `PASS`
- sealed 1239: unchanged
- settlement/KTS/Fixed/Linked: unchanged
- Official Engine semantics: unchanged
- Registry/Master/EXP results: unchanged
- prospective source log/state: unchanged

## Final integrity hashes

- canonical CSV: `56748e0192252706d2cf90c6306aff9b8c6c88381a90624c27f4fb23713ca27c`
- canonical SQLite: `c4e131a47518c54ddc7c2a50b21bdaa95ae102743aac64da5b6ebf63723a7404`
- prospective log: `308e1ea65fd2d4953c8d2e50120f74f8dee3ecf8821cc673495ea5bdc9e9f903`
- prospective state 002: `eac2ead0c0ca3130a629fd86271d3abb22a0ab47c200d0aca278290a55514891`
- sealed 1239: `ed23691c5b9f1715c85b6d3362735dfa8cebb72b31dc258e2aa43bc299c94ead`
- KTS45 schedule: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075`
- locked protocol: `22e8ba6f87d2e1e715abb020e59e8c3493dbf641212fbb3507047d0e16e0ecf7`

The protected hashes match the values recorded before this web-only task. No protected source was rewritten.

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .data import DataValidationError, Draw, ENGINE_VERSION, load_and_validate_csv, sha256_file, write_normalized


class CollectionValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = tuple(errors)
        super().__init__("\n".join(errors))


@dataclass(frozen=True)
class DataConflict:
    round: int
    field: str
    official: str
    user: str


class DataConflictError(ValueError):
    def __init__(self, conflicts: list[DataConflict]):
        self.conflicts = tuple(conflicts)
        super().__init__(f"사용자 자료와 공식 자료가 {len(conflicts)}개 항목에서 충돌합니다.")


def _raw_bundle_sha256(raw_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(raw_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file():
            raise CollectionValidationError([f"원본 묶음에 예상하지 못한 항목이 있습니다: {path.name}"])
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_collection_integrity(collection_dir: Path) -> tuple[dict[str, object], Path]:
    errors: list[str] = []
    metadata_path = collection_dir / "metadata.json"
    csv_path = collection_dir / "official.csv"
    raw_dir = collection_dir / "raw"
    for required in (metadata_path, csv_path, raw_dir):
        if not required.exists():
            errors.append(f"수집 묶음 필수 항목이 없습니다: {required.name}")
    if errors:
        raise CollectionValidationError(errors)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CollectionValidationError([f"수집 메타데이터를 읽을 수 없습니다: {exc}"]) from exc

    expected_fields = {
        "source", "source_page", "source_api", "collection_status", "start_round",
        "end_round", "draw_count", "raw_bundle_sha256", "csv_sha256",
    }
    missing = sorted(expected_fields - set(metadata))
    if missing:
        errors.append(f"수집 메타데이터 필드가 부족합니다: {missing}")
    if metadata.get("collection_status") != "COLLECTED_UNVERIFIED":
        errors.append(f"검사할 수 없는 수집 상태입니다: {metadata.get('collection_status')!r}")
    if metadata.get("source") != "동행복권 공식 사이트":
        errors.append(f"공식 출처 표시가 올바르지 않습니다: {metadata.get('source')!r}")
    if metadata.get("csv_sha256") != sha256_file(csv_path):
        errors.append("수집 후 official.csv 내용이 변경되었습니다.")
    if raw_dir.is_dir() and metadata.get("raw_bundle_sha256") != _raw_bundle_sha256(raw_dir):
        errors.append("수집 후 공식 원본 묶음 내용이 변경되었습니다.")
    if errors:
        raise CollectionValidationError(errors)
    return metadata, csv_path


def validate_official_draws(draws: list[Draw], metadata: dict[str, object]) -> None:
    errors: list[str] = []
    if draws[0].round != 1:
        errors.append(f"공식 데이터 시작 회차가 1회가 아닙니다: {draws[0].round}회")
    if draws[-1].round != metadata.get("end_round"):
        errors.append("CSV 종료 회차와 수집 메타데이터 종료 회차가 다릅니다.")
    if len(draws) != metadata.get("draw_count"):
        errors.append("CSV 유효 회차 수와 수집 메타데이터 회차 수가 다릅니다.")
    for draw in draws:
        if draw.draw_date is None:
            errors.append(f"{draw.round}회 공식 추첨일이 없습니다.")
    for previous, current in zip(draws, draws[1:]):
        if previous.draw_date is not None and current.draw_date is not None:
            if current.draw_date - previous.draw_date != timedelta(days=7):
                errors.append(
                    f"회차와 날짜 간격 오류: {previous.round}회 {previous.draw_date} / "
                    f"{current.round}회 {current.draw_date}"
                )
    if errors:
        raise CollectionValidationError(errors)


def compare_user_data(official: list[Draw], user: list[Draw]) -> list[DataConflict]:
    conflicts: list[DataConflict] = []
    official_by_round = {draw.round: draw for draw in official}
    user_by_round = {draw.round: draw for draw in user}
    if set(official_by_round) != set(user_by_round):
        for round_no in sorted(set(official_by_round) - set(user_by_round)):
            conflicts.append(DataConflict(round_no, "round", "존재", "누락"))
        for round_no in sorted(set(user_by_round) - set(official_by_round)):
            conflicts.append(DataConflict(round_no, "round", "없음", "존재"))
    for round_no in sorted(set(official_by_round) & set(user_by_round)):
        left, right = official_by_round[round_no], user_by_round[round_no]
        if left.draw_date != right.draw_date:
            conflicts.append(DataConflict(round_no, "date", str(left.draw_date), str(right.draw_date)))
        if tuple(sorted(left.main)) != tuple(sorted(right.main)):
            conflicts.append(
                DataConflict(round_no, "main", str(list(sorted(left.main))), str(list(sorted(right.main))))
            )
        if left.bonus != right.bonus:
            conflicts.append(DataConflict(round_no, "bonus", str(left.bonus), str(right.bonus)))
    return conflicts


def validate_collected_dataset(
    collection_dir: Path,
    output_root: Path,
    *,
    user_csv: Path | None = None,
) -> Path:
    metadata, official_csv = validate_collection_integrity(collection_dir)
    try:
        official = load_and_validate_csv(official_csv)
    except DataValidationError as exc:
        raise CollectionValidationError(list(exc.errors)) from exc
    validate_official_draws(official, metadata)

    user_hash: str | None = None
    if user_csv is not None:
        try:
            user = load_and_validate_csv(user_csv)
        except DataValidationError as exc:
            raise CollectionValidationError([f"사용자 자료: {error}" for error in exc.errors]) from exc
        conflicts = compare_user_data(official, user)
        if conflicts:
            raise DataConflictError(conflicts)
        user_hash = sha256_file(user_csv)

    dataset_id = f"validated-1-{official[-1].round}"
    final_dir = output_root / dataset_id
    staging = output_root / f".{dataset_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 확정된 검사 결과가 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 검사 묶음이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        normalized_path = staging / "normalized.csv"
        write_normalized(official, normalized_path)
        report = {
            "status": "PASS",
            "checks": {
                "collection_hashes": "PASS",
                "csv_schema_and_parse": "PASS",
                "round_continuity": "PASS",
                "main_numbers": "PASS",
                "bonus_number": "PASS",
                "date_round_alignment": "PASS",
                "normalization": "PASS",
                "user_data_comparison": "PASS" if user_csv else "NOT_PROVIDED",
            },
        }
        (staging / "validation-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        confirmed = {
            "engine_version": ENGINE_VERSION,
            "confirmation_status": "CONFIRMED",
            "analysis_allowed": True,
            "data_source": "동행복권 공식 사이트",
            "source_collection": str(collection_dir.resolve()),
            "source_raw_bundle_sha256": metadata["raw_bundle_sha256"],
            "source_csv_sha256": metadata["csv_sha256"],
            "user_data_compared": user_csv is not None,
            "user_data_sha256": user_hash,
            "start_round": official[0].round,
            "end_round": official[-1].round,
            "valid_draw_count": len(official),
            "normalized_sha256": sha256_file(normalized_path),
            "confirmed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(confirmed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return final_dir


def write_conflict_report(path: Path, conflicts: tuple[DataConflict, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "status": "CONFLICT",
        "analysis_allowed": False,
        "conflict_count": len(conflicts),
        "conflicts": [asdict(conflict) for conflict in conflicts],
    }
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .data import DataValidationError, prepare_dataset
from .fetch import FetchError, fetch_official_draws
from .validate import (
    CollectionValidationError,
    DataConflictError,
    validate_collected_dataset,
    write_conflict_report,
)
from .structure import StructureAnalysisError, analyze_structure
from .backtest import BacktestError, run_backtest
from .candidates import CandidateGateError, evaluate_candidates
from .selection import SelectionError, create_selection
from .placement import PlacementError, create_set_placement
from .ledger import LedgerError, lock_analysis, review_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="p45", description="P45 Research Engine")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="CSV 데이터를 검사하고 분석 묶음을 확정합니다.")
    prepare.add_argument("--input", required=True, type=Path)
    prepare.add_argument("--output", required=True, type=Path)
    prepare.add_argument("--source", required=True)
    fetch = commands.add_parser("fetch", help="동행복권 공식 당첨번호를 수집합니다.")
    fetch.add_argument("--output", required=True, type=Path)
    validate = commands.add_parser("validate", help="수집 데이터를 검사하고 분석용으로 확정합니다.")
    validate.add_argument("--collection", required=True, type=Path)
    validate.add_argument("--output", required=True, type=Path)
    validate.add_argument("--user-csv", type=Path)
    structure = commands.add_parser("structure", help="확정 데이터의 기본 구조를 분석합니다.")
    structure.add_argument("--dataset", required=True, type=Path)
    structure.add_argument("--output", required=True, type=Path)
    structure.add_argument("--target-round", type=int)
    backtest = commands.add_parser("backtest", help="과거 회차 순차검증을 실행합니다.")
    backtest.add_argument("--structure", required=True, type=Path)
    backtest.add_argument("--output", required=True, type=Path)
    candidates = commands.add_parser("candidates", help="복귀 및 비복귀 후보 관문을 판정합니다.")
    candidates.add_argument("--structure", required=True, type=Path)
    candidates.add_argument("--backtest", required=True, type=Path)
    candidates.add_argument("--output", required=True, type=Path)
    select = commands.add_parser("select", help="공식 및 MIXED_TEST 최종 6개를 선택합니다.")
    select.add_argument("--candidates", required=True, type=Path)
    select.add_argument("--output", required=True, type=Path)
    place = commands.add_parser("place", help="최종 6개를 두 세트로 배치합니다.")
    place.add_argument("--selection", required=True, type=Path)
    place.add_argument("--candidates", required=True, type=Path)
    place.add_argument("--output", required=True, type=Path)
    lock = commands.add_parser("lock", help="분석 전체를 불변 성과 장부에 잠급니다.")
    lock.add_argument("--dataset", required=True, type=Path)
    lock.add_argument("--structure", required=True, type=Path)
    lock.add_argument("--backtest", required=True, type=Path)
    lock.add_argument("--candidates", required=True, type=Path)
    lock.add_argument("--selection", required=True, type=Path)
    lock.add_argument("--sets", required=True, type=Path)
    lock.add_argument("--ledger", required=True, type=Path)
    review = commands.add_parser("review", help="실제 결과를 별도 기록으로 복기합니다.")
    review.add_argument("--ledger", required=True, type=Path)
    review.add_argument("--round", required=True, type=int)
    review.add_argument("--main", required=True, type=int, nargs=6)
    review.add_argument("--bonus", required=True, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare":
        try:
            result = prepare_dataset(args.input, args.output, args.source)
        except DataValidationError as exc:
            print("데이터 검사 실패 — 공식 분석을 중단합니다.", file=sys.stderr)
            for error in exc.errors:
                print(f"- {error}", file=sys.stderr)
            return 2
        except (OSError, FileExistsError) as exc:
            print(f"데이터 확정 실패: {exc}", file=sys.stderr)
            return 3
        metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
        print(f"데이터 확정 완료: {result}")
        print(f"범위: {metadata['start_round']}~{metadata['end_round']}회 ({metadata['valid_draw_count']}건)")
        print(f"원본 SHA-256: {metadata['raw_sha256']}")
        print(f"정규화 SHA-256: {metadata['normalized_sha256']}")
        return 0
    if args.command == "fetch":
        try:
            result = fetch_official_draws(args.output)
        except FetchError as exc:
            print(f"공식 데이터 수집 실패 — 저장을 확정하지 않습니다: {exc}", file=sys.stderr)
            return 4
        except (OSError, FileExistsError) as exc:
            print(f"공식 데이터 저장 실패: {exc}", file=sys.stderr)
            return 3
        metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
        print(f"공식 데이터 수집 완료: {result}")
        print(f"범위: 1~{metadata['end_round']}회 ({metadata['draw_count']}건)")
        print("상태: 수집 완료 / 페이즈 3 데이터 검사 전")
        return 0
    if args.command == "validate":
        try:
            result = validate_collected_dataset(
                args.collection, args.output, user_csv=args.user_csv
            )
        except DataConflictError as exc:
            report = args.output / "conflict-report.json"
            write_conflict_report(report, exc.conflicts)
            print("데이터 충돌 — 공식 확정과 분석을 중단합니다.", file=sys.stderr)
            for conflict in exc.conflicts[:20]:
                print(
                    f"- {conflict.round}회 {conflict.field}: "
                    f"공식={conflict.official} / 사용자={conflict.user}", file=sys.stderr
                )
            print(f"충돌 보고서: {report}", file=sys.stderr)
            return 5
        except CollectionValidationError as exc:
            print("데이터 검사 실패 — 공식 분석을 중단합니다.", file=sys.stderr)
            for error in exc.errors:
                print(f"- {error}", file=sys.stderr)
            return 2
        except (OSError, FileExistsError) as exc:
            print(f"데이터 확정 실패: {exc}", file=sys.stderr)
            return 3
        confirmed = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
        print(f"데이터 검사 통과: {result}")
        print(f"범위: 1~{confirmed['end_round']}회 ({confirmed['valid_draw_count']}건)")
        print(f"정규화 SHA-256: {confirmed['normalized_sha256']}")
        print("상태: CONFIRMED / 분석 사용 가능")
        return 0
    if args.command == "structure":
        try:
            result = analyze_structure(
                args.dataset, args.output, target_round=args.target_round
            )
        except (StructureAnalysisError, DataValidationError) as exc:
            print(f"기본 구조 분석 실패: {exc}", file=sys.stderr)
            return 6
        except (OSError, FileExistsError) as exc:
            print(f"구조 분석 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "structure-report.json").read_text(encoding="utf-8"))
        previous = report["previous_draw_structure"]
        print(f"기본 구조 분석 완료: {result}")
        print(f"분석 대상: {report['target_round']}회 / 사용 데이터: 1~{previous['round']}회")
        print(f"9단위 점유 벡터: {previous['occupancy_9']}")
        print(f"전멸구간: {previous['annihilated_9']}")
        print("후보 판정: 수행하지 않음")
        return 0
    if args.command == "backtest":
        try:
            result = run_backtest(args.structure, args.output)
        except BacktestError as exc:
            print(f"과거 회차 시험 실패: {exc}", file=sys.stderr)
            return 7
        except (OSError, FileExistsError) as exc:
            print(f"과거 회차 시험 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "backtest-report.json").read_text(encoding="utf-8"))
        overall = report["periods"]["overall"]
        print(f"과거 회차 시험 완료: {result}")
        print(f"순차검증 사건 수: {overall['sample_count']}")
        print(f"통합 복귀율: {overall['integrated']['return_rate']:.6f}")
        print(f"본번호 복귀율: {overall['main']['return_rate']:.6f}")
        print(f"미래 데이터 차단: {report['leakage_audit']['status']}")
        print("공식 후보 관문: HOLD / 페이즈 6 후보 노출 전")
        return 0
    if args.command == "candidates":
        try:
            result = evaluate_candidates(args.structure, args.backtest, args.output)
        except CandidateGateError as exc:
            print(f"후보 판정 실패: {exc}", file=sys.stderr)
            return 8
        except (OSError, FileExistsError, DataValidationError) as exc:
            print(f"후보 판정 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "candidate-report.json").read_text(encoding="utf-8"))
        print(f"후보 판정 완료: {result}")
        print(f"복귀 초기 후보: {report['return_candidate_numbers']}")
        print(f"공식 PASS 후보: {report['official_pass_candidates']}")
        print(f"유효 비복귀 TEST 후보: {report['valid_test_candidates']}")
        print(f"공식 후보 결과: {report['official_candidate_result']}")
        return 0
    if args.command == "select":
        try:
            result = create_selection(args.candidates, args.output)
        except SelectionError as exc:
            print(f"최종 후보 선택 실패: {exc}", file=sys.stderr)
            return 9
        except (OSError, FileExistsError) as exc:
            print(f"최종 후보 선택 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "selection-report.json").read_text(encoding="utf-8"))
        print(f"최종 후보 선택 완료: {result}")
        print(f"공식 상태: {report['official_status']}")
        print(f"MIXED_TEST 상태: {report['mixed_test_status']}")
        print(f"최종 숫자: {report['selected_numbers']}")
        print(f"강제 충원: {report['forced_fill_performed']}")
        return 0
    if args.command == "place":
        try:
            result = create_set_placement(args.selection, args.candidates, args.output)
        except PlacementError as exc:
            print(f"세트 배치 실패: {exc}", file=sys.stderr)
            return 10
        except (OSError, FileExistsError) as exc:
            print(f"세트 배치 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "set-report.json").read_text(encoding="utf-8"))
        print(f"두 세트 배치 완료: {result}")
        print(f"배치 상태: {report['placement_status']}")
        print(f"세트1: {report['set_1']}")
        print(f"세트2: {report['set_2']}")
        print(f"후보 교체: {report['candidate_replacement_performed']}")
        return 0
    if args.command == "lock":
        try:
            result = lock_analysis(
                dataset_dir=args.dataset,
                structure_dir=args.structure,
                backtest_dir=args.backtest,
                candidate_dir=args.candidates,
                selection_dir=args.selection,
                sets_dir=args.sets,
                ledger_root=args.ledger,
            )
        except LedgerError as exc:
            print(f"분석 잠금 실패: {exc}", file=sys.stderr)
            return 11
        except (OSError, FileExistsError) as exc:
            print(f"분석 잠금 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "locked-report.json").read_text(encoding="utf-8"))
        print(f"분석 잠금 완료: {result}")
        print(f"대상 회차: {report['target_round']}회")
        print(report["previous_review"])
        print(f"선택 상태: {report['selection']['official_status']}")
        print("잠금 상태: LOCKED")
        return 0
    if args.command == "review":
        try:
            result = review_result(args.ledger, args.round, args.main, args.bonus)
        except LedgerError as exc:
            print(f"결과 복기 실패: {exc}", file=sys.stderr)
            return 12
        except (OSError, FileExistsError) as exc:
            print(f"결과 복기 저장 실패: {exc}", file=sys.stderr)
            return 3
        report = json.loads((result / "review.json").read_text(encoding="utf-8"))
        print(f"결과 복기 완료: {result}")
        print(f"본번호 적중: {report['main_hit_count']}")
        print(f"보너스 적중: {report['bonus_hit']}")
        print(f"통합 적중: {report['integrated_hit_count']}")
        print("과거 잠금 기록 수정: False")
        return 0
    return 1

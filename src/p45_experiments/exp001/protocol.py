from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .constants import EXPERIMENT_ID, PROTOCOL_VERSION
from .snapshot import ROOT, file_sha256

PROTOCOL_DIR = ROOT / "00_P45_STATE/experiment_lab/EXP-001_NUMBER_COOCCURRENCE"
PROTOCOL_FILES = (
    "EXP001_01_PREREGISTRATION.md",
    "EXP001_02_METRIC_DEFINITION.md",
    "EXP001_03_NULL_AND_MULTIPLE_TEST_POLICY.md",
    "EXP001_04_WALKFORWARD_DESIGN.md",
    "EXP001_05_SUCCESS_FAILURE_CRITERIA.md",
)
LOCK_PATH = PROTOCOL_DIR / "EXP001_PROTOCOL_LOCK.json"


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_protocol_texts() -> None:
    texts = {name: (PROTOCOL_DIR / name).read_text(encoding="utf-8-sig") for name in PROTOCOL_FILES}
    required = {
        "EXP001_01_PREREGISTRATION.md": ("990", "MAIN", "INTEGRATED", "RECENT_20", "DESIGNED"),
        "EXP001_02_METRIC_DEFINITION.md": ("1/66", "7/330", "risk_difference", "Holm"),
        "EXP001_03_NULL_AND_MULTIPLE_TEST_POLICY.md": ("IID_FAIR_DRAW_NULL", "maxT", "100,000", "450990001"),
        "EXP001_04_WALKFORWARD_DESIGN.md": ("source_end_round=R-1", "prediction", "R+1"),
        "EXP001_05_SUCCESS_FAILURE_CRITERIA.md": ("READY_FOR_TEST", "BACKTESTED", "SUPPORTED"),
    }
    for name, tokens in required.items():
        for token in tokens:
            if token not in texts[name]:
                raise ValueError(f"PROTOCOL_REQUIRED_TOKEN_MISSING:{name}:{token}")


def create_protocol_lock(data_snapshot_hash: str) -> dict[str, object]:
    validate_protocol_texts()
    documents = [
        {"order": index, "path": f"00_P45_STATE/experiment_lab/EXP-001_NUMBER_COOCCURRENCE/{name}", "sha256": file_sha256(PROTOCOL_DIR / name)}
        for index, name in enumerate(PROTOCOL_FILES, 1)
    ]
    canonical_payload = {
        "experiment_id": EXPERIMENT_ID,
        "protocol_version": PROTOCOL_VERSION,
        "documents": documents,
        "data_snapshot_sha256": data_snapshot_hash,
        "main_baseline": "1/66",
        "integrated_baseline": "7/330",
        "primary_metric": "RISK_DIFFERENCE",
        "multiple_test": "HOLM_FWER_0.05",
        "primary_null": "IID_FAIR_DRAW_NULL",
        "maxT_repetitions": 100000,
        "maxT_seed": 450990001,
        "recent20_policy": "TEST_ONLY",
        "mutation_policy": "NEW_EXPERIMENT_VERSION_REQUIRED",
    }
    protocol_hash = hashlib.sha256(canonical_json(canonical_payload).encode("utf-8")).hexdigest()
    manifest = {"status": "LOCKED_BEFORE_BACKTEST", "canonical_protocol_hash": protocol_hash, "canonical_payload": canonical_payload}
    LOCK_PATH.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify_protocol_lock() -> dict[str, object]:
    manifest = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    payload = manifest["canonical_payload"]
    actual = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    if actual != manifest["canonical_protocol_hash"]:
        raise ValueError("PROTOCOL_HASH_MISMATCH")
    for item in payload["documents"]:
        path = ROOT / item["path"]
        if file_sha256(path) != item["sha256"]:
            raise ValueError(f"PROTOCOL_DOCUMENT_CHANGED:{item['path']}")
    return manifest


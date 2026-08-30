import json
import tempfile
from pathlib import Path
import app.audit.hash_chain as hc


def test_audit_record_hash_chain():
    # Test with temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    orig_path = hc.AUDIT_LOG_PATH
    try:
        hc.AUDIT_LOG_PATH = tmp_path

        # Record 1
        r1 = hc.append_audit_record(
            ingestion_id="ING-1001",
            wbs_activity_id="CIV-STR-010",
            action_performed="Updated to 100%",
            confidence_score=95.0,
            approved_by="manager",
        )
        assert r1["log_index"] == 1
        assert r1["previous_hash"] == "0" * 64
        assert len(r1["current_hash"]) == 64

        # Record 2
        r2 = hc.append_audit_record(
            ingestion_id="ING-1002",
            wbs_activity_id="CIV-STR-011",
            action_performed="Updated to 50%",
            confidence_score=80.0,
            approved_by="manager",
        )
        assert r2["log_index"] == 2
        assert r2["previous_hash"] == r1["current_hash"]

        # Verify chain integrity
        res = hc.verify_chain()
        assert res["is_valid"] is True
        assert res["total_records"] == 2
        assert len(res["errors"]) == 0

        # Tamper with record 1 to test tamper detection
        lines = tmp_path.read_text(encoding="utf-8").strip().split("\n")
        tampered_entry = json.loads(lines[0])
        tampered_entry["action_performed"] = "TAMPERED ACTION"
        lines[0] = json.dumps(tampered_entry)
        tmp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        tamper_res = hc.verify_chain()
        assert tamper_res["is_valid"] is False
        assert len(tamper_res["errors"]) > 0

    finally:
        hc.AUDIT_LOG_PATH = orig_path
        if tmp_path.exists():
            tmp_path.unlink()

"""Offline Chapter 3 companion safety checks; makes NO Snowflake requests.

Static inspection is necessary but not sufficient for safe deployment. It does
not parse the entire Snowflake SQL grammar or verify any live privileges.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SQL = ROOT / "sql"
FILES = ["01_bootstrap.sql", "02_grants.sql", "03_verify.sql", "04_negative_test.sql", "99_cleanup.sql"]

def active_sql(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("--"))


def check() -> None:
    for name in FILES:
        path = SQL / name
        assert path.is_file(), f"Missing companion script: {name}"
        content = path.read_text(encoding="utf-8")
        assert content.strip(), f"Empty companion script: {name}"
        runnable = active_sql(content).upper()
        for forbidden in ["DROP DATABASE", "DROP ROLE", "DROP RESOURCE MONITOR", "ACCOUNTADMIN"]:
            assert forbidden not in runnable, f"Manual audit required: {name}: {forbidden}"
        if name != "99_cleanup.sql":
            assert "BOOK_CH03" in runnable, f"Unexpected non-scoped script: {name}"
    bootstrap = active_sql((SQL / "01_bootstrap.sql").read_text(encoding="utf-8")).upper()
    assert "WAREHOUSE_SIZE = 'XSMALL'" in bootstrap
    assert "AUTO_SUSPEND = 60" in bootstrap
    assert "INITIALLY_SUSPENDED = TRUE" in bootstrap
    assert "82.0" in bootstrap and "SYNTHETIC_WIND" in bootstrap
    reader = active_sql((SQL / "02_grants.sql").read_text(encoding="utf-8")).upper()
    assert "GRANT SELECT ON TABLE" in reader
    assert "GRANT INSERT" not in reader
    cleanup = active_sql((SQL / "99_cleanup.sql").read_text(encoding="utf-8")).upper()
    assert "DROP " not in cleanup, "Cleanup must be read-only until an administrator enables it"
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "SNOWFLAKE_ACCOUNT=" in env_example
    assert "SNOWFLAKE_USER=" in env_example
    assert not re.search(r"(?im)^SNOWFLAKE_(ACCOUNT|USER|PASSWORD|TOKEN)=\S+", env_example)
    print("PASS: chapter 03 offline static preflight (NO live Snowflake execution)")


if __name__ == "__main__":
    check()

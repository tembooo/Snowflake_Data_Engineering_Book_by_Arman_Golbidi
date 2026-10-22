from pathlib import Path
from validate_fixture import generate_manifest

base = Path(__file__).resolve().parent
generate_manifest(base / "data", base / "source_manifest.csv")
print("Generated:", base / "source_manifest.csv")

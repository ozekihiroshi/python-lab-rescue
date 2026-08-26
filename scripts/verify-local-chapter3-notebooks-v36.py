import json
from pathlib import Path


root = Path("/volume")
expected = {
    "07_tables_csv_pandas.ipynb": 6,
    "08_filtering_boolean_logic.ipynb": 7,
    "09_cleaning_audit_trail.ipynb": 8,
    "10_grouping_statistics.ipynb": 7,
}

for language in ("", "ja"):
    directory = root / language
    for name, count in expected.items():
        path = directory / name
        document = json.loads(path.read_text(encoding="utf-8"))
        headings = [
            "".join(cell.get("source", [])).splitlines()[0]
            for cell in document["cells"]
            if cell["cell_type"] == "markdown"
            and "".join(cell.get("source", [])).startswith("## 3.")
        ]
        if len(headings) != count:
            raise RuntimeError(f"{path}: expected {count} numbered topics, found {len(headings)}")
        print(f"ok: {path} — {headings[0]} … {headings[-1]}")

import json
from pathlib import Path


root = Path("/volume")
expected = {
    "07_tables_csv_pandas.ipynb": 6,
    "08_filtering_boolean_logic.ipynb": 7,
    "09_cleaning_audit_trail.ipynb": 7,
    "10_grouping_statistics.ipynb": 6,
}

for language in ("", "ja"):
    directory = root / language
    for name, count in expected.items():
        path = directory / name
        document = json.loads(path.read_text(encoding="utf-8"))
        markdown = [
            "".join(cell.get("source", []))
            for cell in document["cells"]
            if cell["cell_type"] == "markdown"
        ]
        numbered = [
            text.splitlines()[0]
            for text in markdown
            if text.startswith("## 3.")
        ]
        if len(numbered) != count:
            raise RuntimeError(
                f"{path}: expected {count} numbered groups, found {len(numbered)}"
            )

        # Notebook wording is intentionally shorter than the Moodle lesson page.
        # Verify structural boundary cells without demanding identical labels.
        if not any("summary" in text.lower() or "まとめ" in text for text in markdown):
            raise RuntimeError(f"{path}: missing summary section")
        if not any(
            "next" in text.lower() or "次" in text or "3.5a" in text.lower()
            for text in markdown
        ):
            raise RuntimeError(f"{path}: missing next-connection section")
        if any(line.startswith("#### ") for text in markdown for line in text.splitlines()):
            raise RuntimeError(f"{path}: unexpected fourth-level heading")

        print(f"ok: {path} - {numbered[0]} ... {numbered[-1]}")


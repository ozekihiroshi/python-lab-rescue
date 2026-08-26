import json
from pathlib import Path


root = Path("/volume")
expected = {
    "01_programs_values_output.ipynb": ("1.1", 4),
    "02_variables_types_calculations.ipynb": ("1.2", 4),
    "03_basic_scalar_types.ipynb": ("1.3", 4),
    "04_strings_input_formatting.ipynb": ("1.4", 6),
    "03_conditions_boundaries.ipynb": ("1.5", 7),
    "04_loops_accumulators.ipynb": ("1.6", 7),
    "05_lists_dictionaries_records.ipynb": ("2.1", 7),
    "06_functions_errors_testing.ipynb": ("2.2", 7),
    "07_files_csv.ipynb": ("2.3", 6),
}

for language in ("", "ja"):
    for name, (number, count) in expected.items():
        path = root / language / name
        document = json.loads(path.read_text(encoding="utf-8"))
        markdown = [
            "".join(cell.get("source", []))
            for cell in document["cells"] if cell.get("cell_type") == "markdown"
        ]
        groups = [text.splitlines()[0] for text in markdown if text.startswith(f"## {number}.")]
        if len(groups) != count:
            raise RuntimeError(f"{path}: expected {count} groups, found {groups}")
        if document.get("metadata", {}).get("pyai", {}).get("structure_revision") != 38:
            raise RuntimeError(f"{path}: revision metadata missing")
        if any(line.startswith("#### ") for text in markdown for line in text.splitlines()):
            raise RuntimeError(f"{path}: unexpected fourth-level heading")
        print(f"ok: {path} - {groups[0]} ... {groups[-1]}")


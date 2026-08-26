from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path("/opt/python-lab/course-materials")
NOTEBOOKS = [
    ROOT / "13_objects_classes.ipynb",
    ROOT / "14_object_state_validation.ipynb",
    ROOT / "15_composition_responsibility.ipynb",
    ROOT / "16_object_persistence_testing.ipynb",
    ROOT / "P4_equipment_lending.ipynb",
    ROOT / "ja" / "13_objects_classes.ipynb",
    ROOT / "ja" / "14_object_state_validation.ipynb",
    ROOT / "ja" / "15_composition_responsibility.ipynb",
    ROOT / "ja" / "16_object_persistence_testing.ipynb",
    ROOT / "ja" / "P4_equipment_lending.ipynb",
]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="chapter4-notebooks-") as output_dir:
        for index, notebook in enumerate(NOTEBOOKS, start=1):
            result = subprocess.run(
                [
                    "jupyter",
                    "nbconvert",
                    "--execute",
                    "--to",
                    "notebook",
                    "--ExecutePreprocessor.timeout=120",
                    "--output-dir",
                    output_dir,
                    "--output",
                    f"executed-{index}.ipynb",
                    str(notebook),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                print(f"[NG] {notebook.relative_to(ROOT)}")
                print(result.stdout)
                print(result.stderr)
                raise SystemExit(result.returncode)
            print(f"[OK] {notebook.relative_to(ROOT)}")
    print("ALL CHAPTER 4 NOTEBOOKS PASSED")


if __name__ == "__main__":
    main()

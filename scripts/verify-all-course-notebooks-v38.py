import shutil
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient


source = Path("/opt/python-lab/course-materials")
with tempfile.TemporaryDirectory(prefix="python-lab-v38-") as temporary:
    root = Path(temporary) / "course-materials"
    shutil.copytree(source, root)
    notebooks = sorted(root.rglob("*.ipynb"))
    for path in notebooks:
        document = nbformat.read(path, as_version=4)
        client = NotebookClient(
            document,
            timeout=180,
            kernel_name="python3",
            allow_errors=True,
            resources={"metadata": {"path": str(path.parent)}},
        )
        client.execute()
        print(f"executed: {path.relative_to(root)}")
    print(f"executed notebooks: {len(notebooks)}")


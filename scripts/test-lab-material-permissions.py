import os
import subprocess
import tempfile
from pathlib import Path

hook = '/usr/local/bin/start-notebook.d/10-python-lab-materials.sh'
with tempfile.TemporaryDirectory() as home:
    env = dict(os.environ, HOME=home)
    subprocess.run(['sh', hook], env=env, check=True)
    work = Path(home) / 'work'
    target = work / 'ja/projects/school-meal-review/inspect_school_meals.py'
    assert os.access(target, os.W_OK)
    assert os.access(target.parent, os.W_OK)
    original = target.read_bytes()
    edited = original + b'\n# preservation-test\n'
    target.write_bytes(edited)
    target.chmod(0o444)
    target.parent.chmod(0o555)
    subprocess.run(['sh', hook], env=env, check=True)
    assert target.read_bytes() == edited
    assert os.access(target, os.W_OK)
    assert os.access(target.parent, os.W_OK)
    source = Path('/opt/python-lab/course-materials/ja/projects/school-meal-review/inspect_school_meals.py')
    assert source.read_bytes() == original
    assert not os.access(source, os.W_OK)
    print('PASS: fresh copy writable; restart preserves edits and repairs permissions; source unchanged/read-only')

"""Offline smoke test for a newly built image; no learner volume or host ports."""
import io
import json
import os
import subprocess
import tempfile
import time
import urllib.request
from importlib.metadata import version
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

expected = {'jupyterhub': '5.5.0', 'pandas': '3.0.2',
            'matplotlib': '3.10.8', 'openpyxl': '3.1.5'}
assert os.getuid() != 0, 'Must test as the learner user'
assert {key: version(key) for key in expected} == expected
subprocess.run(['python', '-m', 'pip', 'check'], check=True)
frame = pd.read_csv(io.StringIO('school,meals\nA,10\nB,20\n'))
assert frame.meals.sum() == 30
excel = io.BytesIO()
frame.to_excel(excel, index=False, engine='openpyxl')
excel.seek(0)
assert pd.read_excel(excel, engine='openpyxl').equals(frame)
fig, ax = plt.subplots()
ax.plot(frame.meals)
png = io.BytesIO()
fig.savefig(png, format='png')
plt.close(fig)
assert png.getvalue().startswith(b'\x89PNG')
with tempfile.TemporaryDirectory() as root:
    # Fixed synthetic token is confined to this network-isolated test process.
    config = Path(root) / 'jupyter_config.py'
    config.write_text("c.IdentityProvider.token = 'image-smoke-only'\n")
    server = subprocess.Popen([
        'jupyter', 'lab', '--no-browser', '--ip=127.0.0.1', '--port=8899',
        '--ServerApp.port_retries=0', '--ServerApp.root_dir=' + root,
        '--config=' + str(config),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError('JupyterLab exited before becoming ready')
            try:
                req = urllib.request.Request('http://127.0.0.1:8899/api/status',
                    headers={'Authorization': 'token image-smoke-only'})
                with urllib.request.urlopen(req, timeout=1) as response:
                    assert response.status == 200
                    break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError('JupyterLab did not become ready within 60 seconds')
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
print(json.dumps({'versions': expected, 'uid': os.getuid(),
    'csv_excel_plot': 'PASS', 'jupyterlab_authenticated_status': 'PASS'}))

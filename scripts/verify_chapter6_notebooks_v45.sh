#!/bin/sh
set -eu

cp -R /opt/python-lab/course-materials /tmp/course-materials
chmod -R u+w /tmp/course-materials
cd /tmp/course-materials

for notebook in \
  20_inspect_before_loading.ipynb \
  21_chunked_aggregation.ipynb \
  22_reconcile_reproduce.ipynb \
  P6_clinic_stock_scaleup.ipynb \
  ja/20_inspect_before_loading.ipynb \
  ja/21_chunked_aggregation.ipynb \
  ja/22_reconcile_reproduce.ipynb \
  ja/P6_clinic_stock_scaleup.ipynb
do
  jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=240 "${notebook}" >/dev/null
  echo "[OK] ${notebook}"
done

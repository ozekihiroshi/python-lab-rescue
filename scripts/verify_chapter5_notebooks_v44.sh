#!/bin/sh
set -eu

cp -R /opt/python-lab/course-materials /tmp/course-materials
chmod -R u+w /tmp/course-materials
cd /tmp/course-materials

for notebook in \
  17_question_to_chart.ipynb \
  18_honest_comparisons.ipynb \
  19_evidence_statements.ipynb \
  P5_clinic_wait_evidence.ipynb \
  ja/17_question_to_chart.ipynb \
  ja/18_honest_comparisons.ipynb \
  ja/19_evidence_statements.ipynb \
  ja/P5_clinic_wait_evidence.ipynb
do
  jupyter nbconvert \
    --to notebook \
    --execute \
    --inplace \
    --ExecutePreprocessor.timeout=180 \
    "${notebook}" >/dev/null
  echo "[OK] ${notebook}"
done

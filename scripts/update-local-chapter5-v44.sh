#!/bin/sh
set -eu

# Add Chapter 5 materials to an existing learner volume without replacing
# any notebook or project file the learner may already have edited.
for language in "" "ja/"
do
  for notebook in 17_question_to_chart.ipynb 18_honest_comparisons.ipynb 19_evidence_statements.ipynb P5_clinic_wait_evidence.ipynb
  do
    relative="${language}${notebook}"
    source="/opt/python-lab/course-materials/${relative}"
    destination="/volume/${relative}"
    mkdir -p "$(dirname "${destination}")"
    if ! test -e "${destination}"; then
      cp "${source}" "${destination}"
    fi
  done

  relative="${language}projects/clinic-wait-evidence"
  source="/opt/python-lab/course-materials/${relative}"
  destination="/volume/${relative}"
  mkdir -p "${destination}"
  cp -R --update=none "${source}/." "${destination}/"
done

chown -R 1000:100 /volume
chmod -R u+rw /volume

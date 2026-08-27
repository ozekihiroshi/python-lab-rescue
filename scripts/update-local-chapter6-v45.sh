#!/bin/sh
set -eu

# Add Chapter 6 materials without replacing learner-edited files.
for language in "" "ja/"
do
  for notebook in 20_inspect_before_loading.ipynb 21_chunked_aggregation.ipynb 22_reconcile_reproduce.ipynb P6_clinic_stock_scaleup.ipynb
  do
    relative="${language}${notebook}"
    source="/opt/python-lab/course-materials/${relative}"
    destination="/volume/${relative}"
    mkdir -p "$(dirname "${destination}")"
    if ! test -e "${destination}"; then
      cp "${source}" "${destination}"
    fi
  done

  relative="${language}projects/clinic-stock-scaleup"
  source="/opt/python-lab/course-materials/${relative}"
  destination="/volume/${relative}"
  mkdir -p "${destination}"
  cp -R --update=none "${source}/." "${destination}/"
done

chown -R 1000:100 /volume
chmod -R u+rw /volume

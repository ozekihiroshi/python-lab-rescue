#!/bin/sh
set -eu

# Add the new 3.5B/C materials to an existing learner volume without
# replacing any file the learner may already have edited.
for language in "" "ja/"
do
  for notebook in P3B_bus_service_review.ipynb P3C_water_point_review.ipynb
  do
    relative="${language}${notebook}"
    source="/opt/python-lab/course-materials/${relative}"
    destination="/volume/${relative}"
    mkdir -p "$(dirname "${destination}")"
    if ! test -e "${destination}"; then
      cp "${source}" "${destination}"
    fi
  done

  for project in bus-service-review water-point-review
  do
    relative="${language}projects/${project}"
    source="/opt/python-lab/course-materials/${relative}"
    destination="/volume/${relative}"
    mkdir -p "${destination}"
    cp -R --update=none "${source}/." "${destination}/"
  done
done

chown -R 1000:100 /volume
chmod -R u+rw /volume

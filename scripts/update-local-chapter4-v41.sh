#!/bin/sh
set -eu
for language in "" "ja/"
do
  for notebook in 14_object_state_validation.ipynb 15_composition_responsibility.ipynb 16_object_persistence_testing.ipynb P4_equipment_lending.ipynb
  do
    relative="${language}${notebook}"
    destination="/volume/${relative}"
    source="/opt/python-lab/course-materials/${relative}"
    backup="${destination%.ipynb}.pre-v41.ipynb"
    if test -f "${destination}" && ! test -f "${backup}"; then cp -p "${destination}" "${backup}"; fi
    mkdir -p "$(dirname "${destination}")"
    cp "${source}" "${destination}"
    chown 1000:100 "${destination}"; chmod u+rw "${destination}"
  done
  project="${language}projects/equipment-lending"
  if test -f "/volume/${project}/equipment_lending.py" && ! test -f "/volume/${project}/equipment_lending.pre-v41.py"; then
    cp -p "/volume/${project}/equipment_lending.py" "/volume/${project}/equipment_lending.pre-v41.py"
  fi
  mkdir -p "/volume/${project}"
  cp -R "/opt/python-lab/course-materials/${project}/." "/volume/${project}/"
  chown -R 1000:100 "/volume/${project}"
  chmod -R u+rw "/volume/${project}"
done

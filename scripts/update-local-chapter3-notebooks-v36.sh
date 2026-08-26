#!/bin/sh
set -eu

for language in "" "ja/"
do
  for notebook in \
    07_tables_csv_pandas.ipynb \
    08_filtering_boolean_logic.ipynb \
    09_cleaning_audit_trail.ipynb \
    10_grouping_statistics.ipynb
  do
    relative="${language}${notebook}"
    destination="/volume/$relative"
    source="/opt/python-lab/course-materials/$relative"
    backup="${destination%.ipynb}.pre-topic-structure-v36.ipynb"

    test -f "$source"
    if test -f "$destination" && ! test -f "$backup"; then
      cp -p "$destination" "$backup"
    fi
    mkdir -p "$(dirname "$destination")"
    cp "$source" "$destination"
    chown 1000:100 "$destination"
    chmod u+rw "$destination"
    printf '%s\n' "updated: $destination" "backup:  $backup"
  done
done

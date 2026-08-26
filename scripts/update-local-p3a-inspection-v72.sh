#!/bin/sh
set -eu

for language in "" "ja/"
do
  relative="${language}projects/school-meal-review/inspect_school_meals.py"
  destination="/volume/$relative"
  source="/opt/python-lab/course-materials/$relative"
  backup="${destination%.py}.pre-contract-v72.py"

  test -f "$source"
  if test -f "$destination" && ! test -f "$backup"; then
    cp -p "$destination" "$backup"
  fi
  cp "$source" "$destination"
  chown 1000:100 "$destination"
  chmod u+rw "$destination"
  printf '%s\n' "updated: $destination" "backup:  $backup"
done

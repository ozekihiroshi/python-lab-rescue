#!/bin/sh
set -eu

for relative in \
  P3A_school_meal_delivery_review.ipynb \
  ja/P3A_school_meal_delivery_review.ipynb
do
  destination="/volume/$relative"
  source="/opt/python-lab/course-materials/$relative"
  backup="${destination%.ipynb}.pre-observation-v6.ipynb"

  test -f "$source"
  if test -f "$destination" && ! test -f "$backup"; then
    cp -p "$destination" "$backup"
  fi
  cp "$source" "$destination"
  chown 1000:100 "$destination"
  chmod u+rw "$destination"
  printf '%s\n' "updated: $destination" "backup:  $backup"
done

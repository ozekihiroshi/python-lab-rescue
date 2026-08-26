#!/bin/sh
set -eu

for language in "" "ja/"
do
  for notebook in \
    01_programs_values_output.ipynb \
    02_variables_types_calculations.ipynb \
    03_basic_scalar_types.ipynb \
    04_strings_input_formatting.ipynb \
    03_conditions_boundaries.ipynb \
    04_loops_accumulators.ipynb \
    05_lists_dictionaries_records.ipynb \
    06_functions_errors_testing.ipynb \
    07_files_csv.ipynb
  do
    relative="${language}${notebook}"
    destination="/volume/$relative"
    source="/opt/python-lab/course-materials/$relative"
    backup="${destination%.ipynb}.pre-textbook-structure-v38.ipynb"

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


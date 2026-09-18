#!/bin/sh
workdir="${HOME}/work"
sourcedir="/opt/python-lab/course-materials"
marker="${workdir}/.python-lab-materials-v9"

mkdir -p "${workdir}"
# Repair owner permissions on existing copies before adding new materials.
find "${workdir}" -user "$(id -u)" \( -type d -o -type f \) -exec chmod u+rwX {} +
if [ ! -e "${marker}" ]; then
    # Add newly released course files without overwriting learner work.
    cp -R --update=none /opt/python-lab/course-materials/. "${workdir}/"
    # Source materials are read-only; learner copies must remain editable.
    find "${workdir}" -user "$(id -u)" \( -type d -o -type f \) -exec chmod u+rwX {} +
    touch "${marker}"
fi

# Additional self-paced guide, even for learners who already have v9 materials.
# Never replace an edited notebook or any learner program.
for relative in "ja/P1_weekly_support_report_dual_path.ipynb" "P1_weekly_support_report_dual_path.ipynb"
do
if [ -f "${sourcedir}/${relative}" ] && [ ! -e "${workdir}/${relative}" ]; then
    mkdir -p "${workdir}/ja"
    cp --update=none "${sourcedir}/${relative}" "${workdir}/${relative}"
    chmod u+rw "${workdir}/${relative}"
fi
done

# Submission helpers are course infrastructure, not learner work. Keep these
# small managed files current while preserving weekly_support.py and notebooks.
for relative in \
    "projects/weekly-support/submit_weekly_support.py" \
    "ja/projects/weekly-support/submit_weekly_support.py"
do
    sourcepath="${sourcedir}/${relative}"
    destination="${workdir}/${relative}"
    if [ -f "${sourcepath}" ]; then
        mkdir -p "$(dirname "${destination}")"
        cp -f "${sourcepath}" "${destination}"
        chmod u+rw "${destination}"
    fi
done

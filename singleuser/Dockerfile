ARG BASE_IMAGE=quay.io/jupyter/minimal-notebook:2026-07-28@sha256:230b7474518c193143d253822fd86fa0a850aa31e18a74952d940782157d373d
FROM ${BASE_IMAGE}

ARG JUPYTERHUB_VERSION=5.5.0
ARG PANDAS_VERSION=3.0.2
ARG MATPLOTLIB_VERSION=3.10.8
ARG OPENPYXL_VERSION=3.1.5

USER root
RUN python -m pip install --no-cache-dir \
    "jupyterhub==${JUPYTERHUB_VERSION}" \
    "pandas==${PANDAS_VERSION}" \
    "matplotlib==${MATPLOTLIB_VERSION}" \
    "openpyxl==${OPENPYXL_VERSION}"

COPY --chown=${NB_UID}:${NB_GID} course-materials/ /opt/python-lab/course-materials/
COPY singleuser/start-notebook.d/10-python-lab-materials.sh /usr/local/bin/start-notebook.d/10-python-lab-materials.sh
RUN chmod 0755 /usr/local/bin/start-notebook.d/10-python-lab-materials.sh \
    && chmod -R a-w /opt/python-lab/course-materials

USER ${NB_UID}

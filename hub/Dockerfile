FROM jupyterhub/jupyterhub:5.5.0@sha256:f91ed45a0d2333de2ed9f5d708ad6f18a2fb79547526fbaaa19e88fd44fcab71

COPY hub/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY hub/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
COPY hub/moodle-jwks-proxy.py /srv/jupyterhub/moodle-jwks-proxy.py
COPY hub/moodle-submit-service-v2.py /srv/jupyterhub/moodle-submit-service-v2.py

WORKDIR /srv/jupyterhub
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]

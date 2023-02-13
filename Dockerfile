FROM python:3.11.2-slim

ARG USERNAME=appuser
ARG APPDIR=/app

ENV TZ=Asia/Jerusalem

WORKDIR ${APPDIR}
COPY . ${APPDIR}

# These values need to match the user on the host machine
# Should be removed to switch to dynamic values
ARG UID=2000
ARG GID=2000

RUN groupadd --gid ${GID} ${USERNAME} \
  && useradd --no-create-home --home-dir=${APPDIR} --uid=${UID} --gid=${GID} ${USERNAME} \
  && chown -R ${USERNAME}:${USERNAME} ${APPDIR}

RUN python -m pip install --upgrade --no-cache-dir pip \
  && pip install --upgrade --no-cache-dir -r ${APPDIR}/requirements.txt

ENV PYTHONPATH=${APPDIR}
USER ${USERNAME}
EXPOSE 8000
VOLUME [ "/app/npz" ]
CMD [ "uvicorn", "main:app", "--host=0.0.0.0" ]

FROM python:3.9-slim-buster
RUN useradd --create-home app
WORKDIR /usr/src/app
USER app
COPY --chown=app zulip-exporter/. .
RUN pip install -r requirements.txt --no-cache-dir --user
CMD [ "python", "zulip-exporter.py" ]

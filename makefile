envfile := ${HOME}/.secrets/._zuliprc
versionfile := _version
VERSION :=$(file < $(versionfile))
IMAGE := brokenpip3/zulip-exporter

.PHONY: all build push docker-run

all: build push docker-run

build:
	docker build -t $(IMAGE):$(VERSION) . --no-cache

push:
	docker push $(IMAGE):$(VERSION)

docker-run:
	docker run -i -t --rm -p 9863:9863 --env-file=${envfile} $(IMAGE):$(VERSION)


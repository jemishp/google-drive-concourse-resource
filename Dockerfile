FROM python:2.7

RUN apt-get update; apt-get -y upgrade; apt-get clean

RUN pip install --upgrade google-api-python-client

COPY check in out google_drive_concourse_resource_common.py concourse-resource.json tests /opt/resource/

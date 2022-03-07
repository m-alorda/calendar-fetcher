FROM python:3.10-alpine3.15

# Base dependencies
RUN apk update && apk upgrade
RUN python3 -m pip install --upgrade pip
RUN apk add bash git

# Configure bash
COPY .devcontainer/.bashrc /root/.bashrc

# Install python dependencies
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

CMD [ "bash" ]

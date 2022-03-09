FROM python:3.10-alpine3.15

ARG USERNAME=calendar_fetcher
ARG USER_UID=1000
ARG USER_GROUP=${USERNAME}
ARG USER_GID=${USER_UID}

RUN addgroup --gid ${USER_GID} ${USER_GROUP} && \
    adduser --disabled-password --shell /bin/bash --home /home/${USERNAME} --uid ${USER_UID} --ingroup ${USER_GROUP} ${USERNAME}

# Base dependencies
RUN apk update && apk upgrade
RUN python3 -m pip install --upgrade pip
RUN apk add bash git

# Configure bash
COPY .devcontainer/.bashrc /root/.bashrc
COPY .devcontainer/.bashrc /home/${USERNAME}/.bashrc

# Install python dependencies
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

CMD [ "bash" ]

USER ${USERNAME}

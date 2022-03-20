FROM python:3.10-alpine3.15

ARG USERNAME=calendar_fetcher
ARG USER_UID=1000
ARG USER_GROUP=${USERNAME}
ARG USER_GID=${USER_UID}

RUN addgroup --gid ${USER_GID} ${USER_GROUP} && \
    adduser --disabled-password --shell /bin/bash --home /home/${USERNAME} --uid ${USER_UID} --ingroup ${USER_GROUP} ${USERNAME}

# Since the container is running as non-root user, these files have to be created manually and chowned
RUN mkdir -p /home/${USERNAME}/.vscode-server/extensions && \
    chown -R ${USERNAME}:${USER_GROUP} /home/${USERNAME}/.vscode-server && \
    mkdir -p /home/${USERNAME}/.vscode-server-insiders/extensions && \
    chown -R ${USERNAME}:${USER_GROUP} /home/${USERNAME}/.vscode-server-insiders

# Base dependencies
RUN apk update && apk upgrade
RUN python3 -m pip install --upgrade pip
RUN apk add bash git

# Configure bash
COPY .devcontainer/.bashrc /root/.bashrc
COPY .devcontainer/.bashrc /home/${USERNAME}/.bashrc

# Compile dependencies for weasyprint
RUN apk add py3-pillow py3-cffi py3-brotli gcc musl-dev python3-dev pango libffi-dev zlib-dev jpeg-dev
# Fonts for weasyprint
RUN wget https://github.com/google/fonts/archive/main.tar.gz -O gf.tar.gz && \
    tar -xf gf.tar.gz && \
    mkdir -p /usr/share/fonts/truetype/google-fonts && \
    find $PWD/fonts-main/ -name "*.ttf" -exec install -m644 {} /usr/share/fonts/truetype/google-fonts/ \; || return 1 && \
    rm -f gf.tar.gz && \
    # Remove the extracted fonts directory
    rm -rf $PWD/fonts-main && \
    rm -rf /var/cache/* && \
    fc-cache -f

# Install python dependencies
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

# TODO: remove weasyprint compile dependencies

CMD [ "bash" ]

USER ${USERNAME}

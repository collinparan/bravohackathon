FROM linuxserver/code-server:latest

USER root
VOLUME /root
WORKDIR /root

RUN apt update && \
    apt -y install sudo

RUN sudo apt-get update && \
    sudo apt install -y software-properties-common && \
    sudo add-apt-repository ppa:deadsnakes/ppa && \
    sudo apt install -y python3 && \
    rm /usr/bin/python && \
    sudo ln -s /usr/bin/python3 /usr/bin/python && \
    sudo apt install -y python3-pip && \
    sudo ln -s /usr/bin/pip3 /usr/bin/pip && \
    sudo apt-mark hold python python-pip

COPY / ./root

EXPOSE 8443 
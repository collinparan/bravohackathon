FROM linuxserver/code-server:latest

USER root
VOLUME /root
WORKDIR /root

RUN apt update && \
    apt -y install sudo

# RUN sudo apt-get update && \
#     sudo apt install -y software-properties-common && \
#     sudo add-apt-repository ppa:deadsnakes/ppa && \
#     sudo apt install -y python3 && \
#     sudo ln -s /usr/bin/python3 /usr/bin/python && \
#     sudo apt install -y python3-pip && \
#     sudo ln -s /usr/bin/pip3 /usr/bin/pip

COPY ./ ./root

# RUN pip install -r requirements.txt
# RUN chmod u+x app.py 

EXPOSE 8443 
#!/usr/bin/env bash

echo "Building basic container...";
(docker build -t centoscodeserver:latest . -f .Dockerfile);

echo "Running base container...";
(docker run -it --privileged --rm -p 80:80 -p 8080:8080 -p 8443:8443 -e ROOT=TRUE -e SUDO_PASSWORD=123 -v /Users/collinparan/Documents/dockerfiles/bravohackathon/volumes:/root --name centoscodeserver -d centoscodeserver:latest);

# open http://localhost:8443/?folder=/root/python_scripts; 


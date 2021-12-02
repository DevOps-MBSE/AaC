FROM gitpod/workspace-full-vnc

ARG PYTHON_VERSION=3.9

RUN sudo add-apt-repository ppa:deadsnakes/ppa -y
RUN sudo apt install python${PYTHON_VERSION} -y
RUN sudo apt install python${PYTHON_VERSION}-venv -y
RUN sudo apt install python${PYTHON_VERSION}-tk -y
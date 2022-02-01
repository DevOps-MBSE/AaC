FROM gitpod/workspace-full

# Python Dependencies
ARG PYTHON_VERSION=3.9

RUN sudo add-apt-repository ppa:deadsnakes/ppa -y
RUN sudo apt install python${PYTHON_VERSION} -y
RUN sudo apt install python${PYTHON_VERSION}-venv -y

# Typescript Dependencies
RUN sudo apt-get install libnss3-dev libgbm-dev -y
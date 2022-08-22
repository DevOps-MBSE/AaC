FROM gitpod/workspace-full

# Python Dependencies
ARG PYTHON_VERSION=3.9

RUN sudo add-apt-repository ppa:deadsnakes/ppa -y
RUN sudo apt install python${PYTHON_VERSION} -y
RUN sudo apt install python${PYTHON_VERSION}-venv -y
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 2

# Typescript Dependencies
RUN sudo apt-get install libnss3-dev libgbm-dev libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 xvfb -y
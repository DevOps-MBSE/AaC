FROM gitpod/workspace-full

ARG PYTHON_VERSION=3.9

RUN sudo add-apt-repository ppa:deadsnakes/ppa -y
RUN sudo apt install python${PYTHON_VERSION} -y 
RUN sudo rm -rf $(which python)

# TODO: Replace this with virtual environments
RUN sudo mv /usr/bin/python${PYTHON_VERSION} /home/gitpod/.pyenv/shims/python 
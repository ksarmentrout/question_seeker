#! /usr/bin/env bash
set -eo pipefail

###
# Install conda into current user's home directory

export PATH=/usr/local/bin:$HOME/anaconda/bin:$PATH
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -f -b -p $HOME/anaconda \
    && pushd $HOME/anaconda/bin \
    && conda install pip -y \
    && conda clean -i -t -y \
    && conda install -q -y -n root conda-build \
    && conda install -q -y -n root conda-devenv setuptools_scm -c conda-forge\
    && conda init bash \
    && popd \
&& rm miniconda.sh


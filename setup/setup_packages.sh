#! /usr/bin/env bash
set -eo pipefail

########################################################################################
apt-get -q -y update
apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        dvipng \
        git \
        g++ \
        htop \
        libffi-dev \
        libvips-dev \
        libgl1-mesa-glx \
        mysql-server \
        sudo \
        unzip \
        wget \
        zip

apt-get clean
apt-get autoremove --purge


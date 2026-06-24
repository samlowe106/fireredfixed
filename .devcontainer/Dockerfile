# Self-contained build environment for FireRed Fixed.
# Supports BOTH build paths out of the box:
#   make          -> byte-matching build (uses agbcc, pre-built into this image)
#   make modern   -> arm-none-eabi-gcc build
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Host tools (build_tools / gbagfx need a C/C++ compiler + libpng),
# the ARM toolchain (binutils for matching builds, gcc for `make modern`), and git.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        binutils-arm-none-eabi \
        gcc-arm-none-eabi \
        libnewlib-arm-none-eabi \
        libpng-dev \
        git \
        ca-certificates \
        sudo \
    && rm -rf /var/lib/apt/lists/*

# Pre-build agbcc once, here in the image, so container creation is fast. It is
# copied into the workspace's tools/agbcc on first use (dev container postCreate,
# or the build-docker.sh wrapper). Left world-readable so any host UID can copy it.
RUN git clone --depth 1 https://github.com/pret/agbcc /opt/agbcc \
    && cd /opt/agbcc \
    && ./build.sh \
    && chmod -R a+rX /opt/agbcc

# Non-root user; the dev container syncs its UID to the host so files created in
# the bind-mounted repo stay owned by you. (The build-docker.sh wrapper overrides
# the user with the host UID directly, so it doesn't rely on this account.)
ARG USERNAME=vscode
RUN useradd -m -s /bin/bash "$USERNAME" \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/"$USERNAME" \
    && chmod 0440 /etc/sudoers.d/"$USERNAME"
USER $USERNAME

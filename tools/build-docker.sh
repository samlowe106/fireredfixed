#!/usr/bin/env bash
#
# Build FireRed Fixed inside Docker -- no local toolchain required.
# Runs `make <your target/args>` in the container against this repo and writes the
# ROM + build artifacts back here, owned by you. Same on Linux, macOS, and Windows
# (Docker Desktop / WSL2). Supports both build paths: matching (agbcc) and modern.
#
# Usage:
#   tools/build-docker.sh [make targets/args...]
#
# Examples:
#   tools/build-docker.sh                  # default build (FireRed, matching/agbcc)
#   tools/build-docker.sh modern           # build with arm-none-eabi-gcc
#   tools/build-docker.sh leafgreen        # build LeafGreen
#   tools/build-docker.sh firered_rev1 -j8 # a revision, in parallel
#   tools/build-docker.sh compare          # build + verify against the original ROM
#   tools/build-docker.sh clean
#
# Env:
#   IMAGE   override the image tag (default: fireredfixed-build)
#   DOCKER  override the docker command (e.g. "podman")
#
set -euo pipefail

IMAGE="${IMAGE:-fireredfixed-build}"
DOCKER="${DOCKER:-docker}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v "$DOCKER" >/dev/null 2>&1; then
    echo "error: '$DOCKER' is not installed or not on PATH." >&2
    echo "Install Docker Desktop (macOS/Windows) or docker.io (Linux), then re-run." >&2
    exit 1
fi

# Build the image once; it is cached afterwards. Same Dockerfile as the dev container.
"$DOCKER" build -t "$IMAGE" "$ROOT/.devcontainer"

# Run as the host user/group so the ROM and *.o files aren't created as root.
# agbcc is copied from the image into tools/agbcc on first use (matching build only).
exec "$DOCKER" run --rm \
    -v "$ROOT:/work" -w /work \
    -u "$(id -u):$(id -g)" -e HOME=/tmp \
    "$IMAGE" \
    bash -c '
        set -e
        if [ ! -x tools/agbcc/bin/agbcc ]; then
            ( cd /opt/agbcc && bash ./install.sh /work )
        fi
        exec make "$@"
    ' bash "$@"

#!/usr/bin/env bash
#
# Native build setup for FireRed Fixed -- installs the toolchain and agbcc so you can
# `make` directly on this machine (no Docker). Re-runnable; skips what's already done.
#
#   Linux (apt):  fully automated.
#   macOS (brew): installs libpng + builds agbcc; points you at devkitPro for the
#                 arm-none-eabi toolchain if it's missing.
#   Windows:      run this inside WSL2 (it's just Linux there).
#
# After this finishes:  make            (matching build, uses agbcc)
#                       make modern     (arm-none-eabi-gcc build)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

install_linux_apt() {
    echo "==> Installing build dependencies via apt..."
    sudo apt-get update
    sudo apt-get install -y build-essential binutils-arm-none-eabi gcc-arm-none-eabi libpng-dev git
}

install_macos() {
    if ! command -v brew >/dev/null 2>&1; then
        echo "error: Homebrew is required (https://brew.sh)." >&2
        exit 1
    fi
    echo "==> Installing libpng via Homebrew..."
    brew install libpng
    if ! command -v arm-none-eabi-gcc >/dev/null 2>&1 && [ ! -d /opt/devkitpro/devkitARM ]; then
        echo
        echo "NOTE: the arm-none-eabi toolchain was not found. Install devkitARM:"
        echo "  https://devkitpro.org/wiki/Getting_Started   then:  sudo dkp-pacman -S gba-dev"
        echo "(needed for the linker, and for 'make modern')."
    fi
}

case "$(uname -s)" in
    Linux)
        if command -v apt-get >/dev/null 2>&1; then
            install_linux_apt
        else
            echo "Non-apt Linux detected. Install these from your package manager, then re-run:"
            echo "  gcc g++ make git libpng-dev  + the arm-none-eabi toolchain (or devkitPro gba-dev)."
            exit 1
        fi
        ;;
    Darwin) install_macos ;;
    *)
        echo "Unsupported OS '$(uname -s)'. On Windows, run this inside WSL2." >&2
        exit 1
        ;;
esac

# Build + install agbcc for the byte-matching build (skipped if already present).
if [ ! -x "$ROOT/tools/agbcc/bin/agbcc" ]; then
    AGBCC_DIR="${AGBCC_DIR:-$ROOT/../agbcc}"
    echo "==> Building agbcc in $AGBCC_DIR ..."
    [ -d "$AGBCC_DIR/.git" ] || git clone --depth 1 https://github.com/pret/agbcc "$AGBCC_DIR"
    ( cd "$AGBCC_DIR" && ./build.sh && ./install.sh "$ROOT" )
else
    echo "==> agbcc already installed (tools/agbcc), skipping."
fi

echo
echo "Done. Build with:"
echo "  make -j\$(getconf _NPROCESSORS_ONLN)          # matching build (agbcc)"
echo "  make modern -j\$(getconf _NPROCESSORS_ONLN)   # arm-none-eabi-gcc"

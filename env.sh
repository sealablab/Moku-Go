#!/usr/bin/env bash

# Source this file from the repository root to configure the local development
# environment for the UV-managed Moku-Go project.

REPO_ROOT="${PWD}"

# Point the Python API at the local bitstream/data directory without invoking
# the upstream mokucli binary (some distributions omit the legacy `config`
# command the API expects).
export MOKU_DATA_PATH="${MOKU_DATA_PATH:-${REPO_ROOT}}"

# Default target device; override as needed.
export MOKU_IP="${MOKU_IP:-192.168.13.159}"

# The mokucli shim is no longer needed as the issue has been resolved
# export MOKU_CLI_PATH="${MOKU_CLI_PATH:-${REPO_ROOT}/scripts/mokucli_shim.py}"

# Keep uv's cache in the project tree to avoid permission issues when running
# inside sandboxed environments.
export UV_CACHE_DIR="${UV_CACHE_DIR:-${REPO_ROOT}/.uv-cache}"

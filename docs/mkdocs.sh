#!/bin/bash

set -Eeuo pipefail

# Get the PROJECT root, not the site directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )" # Go up one level

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # site/ directory
DOCS_DIR="${SCRIPT_DIR}/docs"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Remove existing docs directory
rm -rf "${DOCS_DIR}" || true  # Suppress error if directory doesn't exist

mkdir -p "${DOCS_DIR}"

# Copy assets (if any, adjust path if needed)
if [ -d "${PROJECT_ROOT}/assets" ]; then #checks if dir assets is present
  cp -r "${PROJECT_ROOT}/assets" "${DOCS_DIR}/assets" || true  # Handle potential missing assets dir
fi

# Create and activate virtual environment
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

# Install requirements
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    pip install -r "${SCRIPT_DIR}/requirements.txt" || { echo "pip install failed"; exit 1; }
fi


# Functions using rsync (more efficient)
copy_notebooks() { rsync -a --include='*/' --include='*.ipynb' --exclude='*' "$1" "$2"; }
copy_readme_files() { rsync -a --include='*/' --include='README.md' --exclude='*' "$1" "$2"; }
copy_image_files() { rsync -a --include='*/' --include='*.{png,jpg,jpeg,gif,svg}' --exclude='*' "$1" "$2"; }



# Copy main README.md (from the project root)
cp "${PROJECT_ROOT}/README.md" "${DOCS_DIR}/index.md"
mkdir -p "${DOCS_DIR}/stylesheets"
cp -r "${PROJECT_ROOT}/docs/stylesheets" "${DOCS_DIR}/stylesheets"

# Process each main directory (source files from PROJECT_ROOT)
for dir in ai-infrastructure genai-on-vertex-ai research-operationalization; do
    mkdir -p "${DOCS_DIR}/${dir}"
    copy_readme_files "${PROJECT_ROOT}/${dir}" "${DOCS_DIR}/"
    copy_notebooks "${PROJECT_ROOT}/${dir}" "${DOCS_DIR}/"
    copy_image_files "${PROJECT_ROOT}/${dir}" "${DOCS_DIR}/"
done

# Run mkdocs (cd to the script's directory)
(cd "${SCRIPT_DIR}" && mkdocs "$@")

deactivate
#!/bin/bash

set -Eeuo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOCS_DIR="${SCRIPT_DIR}/docs"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Remove existing docs directory if it exists
if [ -d "${DOCS_DIR}" ]; then
    rm -rf "${DOCS_DIR}"
fi

# Create docs directory
mkdir -p "${DOCS_DIR}"

# Create and activate virtual environment
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

# Install requirements
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
else
    echo "Warning: requirements.txt not found. Skipping package installation."
fi

# Function to copy .ipynb files
copy_notebooks() {
    local src_dir="$1"
    local dest_dir="$2"
    find "${src_dir}" -name "*.ipynb" | while read -r notebook; do
        rel_path="${notebook#${src_dir}/}"
        mkdir -p "${dest_dir}/$(dirname "${rel_path}")"
        cp "${notebook}" "${dest_dir}/${rel_path}"
    done
}

# Function to copy README.md files
copy_readme_files() {
    local src_dir="$1"
    local dest_dir="$2"
    find "${src_dir}" -name "README.md" | while read -r readme; do
        rel_path="${readme#${src_dir}/}"
        mkdir -p "${dest_dir}/$(dirname "${rel_path}")"
        cp "${readme}" "${dest_dir}/${rel_path}"
    done
}

# Function to copy image files
copy_image_files() {
    local src_dir="$1"
    local dest_dir="$2"
    find "${src_dir}" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.svg" \) | while read -r image; do
        rel_path="${image#${src_dir}/}"
        mkdir -p "${dest_dir}/$(dirname "${rel_path}")"
        cp "${image}" "${dest_dir}/${rel_path}"
    done
}

# Copy main README.md
cp "${SCRIPT_DIR}/README.md" "${DOCS_DIR}/index.md"

# Process each main directory
for dir in ai-infrastructure genai-on-vertex-ai research-operationalization; do
    mkdir -p "${DOCS_DIR}/${dir}"
    copy_readme_files "${SCRIPT_DIR}/${dir}" "${DOCS_DIR}/${dir}"
    copy_notebooks "${SCRIPT_DIR}/${dir}" "${DOCS_DIR}/${dir}"
    copy_image_files "${SCRIPT_DIR}/${dir}" "${DOCS_DIR}/${dir}"
done

# Run mkdocs
(cd "${SCRIPT_DIR}" && mkdocs "$@")

# Deactivate virtual environment
deactivate
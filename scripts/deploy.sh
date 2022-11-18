#!/bin/bash

declare -r script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
declare -r base_dir="${script_dir}/.."
declare -r dest_dir="${1:-/media/${USER}/CIRCUITPY}"

source "${base_dir}/venv/bin/activate"

echo "Deploying to Matrix Portal..."
echo
echo "Source Path:    ${base_dir}"
echo "Destination:    ${dest_dir}"
echo

echo "Installing project libraries and dependencies..."
echo
circup install -r "${base_dir}/requirements.txt"
echo

echo "Syncronising project source to destination device (${dest_dir})..."
echo
rsync -av "${base_dir}/src/" "${dest_dir}/"
sync
echo

echo "DONE"
echo
#!/bin/bash

declare -r script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
declare -r base_dir="${script_dir}/.."
declare -r theme="${1:-mario}"
declare -r dest_dir="${2:-/media/${USER}/CIRCUITPY}"


source "${base_dir}/venv/bin/activate"

echo "Deploying to Matrix Portal..."
echo
echo "Theme:          ${theme} (theme_${theme}.py)"
echo "Source Path:    ${base_dir}"
echo "Destination:    ${dest_dir}"
echo

echo "Syncronising project source to destination device (${dest_dir})..."
echo
rsync -av --inplace --exclude "theme_*.py" "${base_dir}/src/" "${dest_dir}/"
cp -v "${base_dir}/src/themes/${theme}.py" "${dest_dir}/theme.py"
cp -v "${base_dir}/src/themes/${theme}.bmp" "${dest_dir}/theme.bmp"
sync
echo

echo "DONE"
echo
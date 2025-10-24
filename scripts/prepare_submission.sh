#!/usr/bin/env bash

set -euo pipefail

show_help() {
  cat <<'USAGE'
Usage: prepare_submission.sh <team-name> [project-root] [output-dir]

Creates a submission archive (<team-name>.tar.gz) following the guidelines in README.md
and project_submission_guide.md, and performs validation checks on the result.

Arguments:
  <team-name>     Name of the team. Determines the archive name (<team-name>.tar.gz).
  [project-root]  Path to the project directory to package. Defaults to current directory.
  [output-dir]    Directory where the archive will be written. Defaults to project root.

The script will:
  1. Verify that main.py and requirements.txt exist at the project root.
  2. Create a tar.gz archive using `tar -czf <team-name>.tar.gz -C <project-root> .`.
  3. Extract the archive into a temporary directory to ensure the required files
     are at the archive root.

On success it prints the archive location and removes any temporary files.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  show_help
  exit 0
fi

if [[ $# -lt 1 || $# > 3 ]]; then
  show_help
  exit 1
fi

TEAM_NAME=$1
PROJECT_ROOT=${2:-.}
OUTPUT_DIR=${3:-$PROJECT_ROOT}
ARCHIVE_NAME="${TEAM_NAME}.tar.gz"
ARCHIVE_PATH="${OUTPUT_DIR%/}/${ARCHIVE_NAME}"

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "ERROR: Project root '$PROJECT_ROOT' does not exist or is not a directory." >&2
  exit 1
fi

if [[ ! -f "$PROJECT_ROOT/main.py" ]]; then
  echo "ERROR: main.py not found in project root '$PROJECT_ROOT'." >&2
  exit 1
fi

if [[ ! -f "$PROJECT_ROOT/requirements.txt" ]]; then
  echo "ERROR: requirements.txt not found in project root '$PROJECT_ROOT'." >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

TMP_ARCHIVE=""
TMP_EXTRACT_DIR=""
cleanup() {
  if [[ -n "$TMP_ARCHIVE" && -f "$TMP_ARCHIVE" ]]; then
    rm -f "$TMP_ARCHIVE"
  fi
  if [[ -n "$TMP_EXTRACT_DIR" && -d "$TMP_EXTRACT_DIR" ]]; then
    rm -rf "$TMP_EXTRACT_DIR"
  fi
}
trap cleanup EXIT

TMP_ARCHIVE=$(mktemp "${TMPDIR:-/tmp}/prepare_submission.XXXXXX")

tar -czf "$TMP_ARCHIVE" -C "$PROJECT_ROOT" .

mv "$TMP_ARCHIVE" "$ARCHIVE_PATH"
TMP_ARCHIVE=""

TMP_EXTRACT_DIR=$(mktemp -d "${TMPDIR:-/tmp}/prepare_submission.XXXXXX")

tar -xzf "$ARCHIVE_PATH" -C "$TMP_EXTRACT_DIR"

if [[ ! -f "$TMP_EXTRACT_DIR/main.py" ]]; then
  echo "ERROR: Extracted archive missing main.py at root." >&2
  exit 1
fi

if [[ ! -f "$TMP_EXTRACT_DIR/requirements.txt" ]]; then
  echo "ERROR: Extracted archive missing requirements.txt at root." >&2
  exit 1
fi

cleanup
trap - EXIT

cat <<EOF_OUT
Submission archive created successfully.
Archive path: $ARCHIVE_PATH
Verified that main.py and requirements.txt are located at the archive root.
EOF_OUT

#! /bin/bash


die() {
  echo "$1" >&2
  exit 1
}

unvenv_die() {
  deactivate
  die "$1"
}

# Test a specific Python version.
#
# Receives the name of the desired python executable file.
#
# Example:
#   test_python "python2"
#   test_python "python3.4"
test_python() {
  local python_exe="$1"
  local status
  local report_to_codacy
  local codacy_deps

  if [[ -n $CODACY_PROJECT_TOKEN ]]; then
    report_to_codacy=1
    codacy_deps="codacy-coverage"
  else
    report_to_codacy=0
    codacy_deps=""
  fi

  venv=$(mktemp -d --tmpdir capidup-venv-XXXXXX) || die "unable to create temp directory"

  virtualenv --python="$python_exe" "$venv"
  source "$venv/bin/activate"

  for i in pytest coverage pytest-cov $codacy_deps .; do
    pip install "$i" || unvenv_die "unable to install $i inside virtualenv"
  done

  py.test --cov=capidup capidup

  if (( report_to_codacy )); then
    coverage xml
    python-codacy-coverage -r coverage.xml
  fi
  status=$?

  deactivate

  rm -rf "$venv"

  return $status
}

if (( $# >= 1 )); then
  # load external script; should define CODACY_PROJECT_TOKEN for test coverage
  # reporting
  source "$1"
fi

test_python "python2"
test_python "python3"

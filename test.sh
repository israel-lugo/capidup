#! /bin/bash


die() {
  echo "$1" >&2
  exit 1
}

unvenv_die() {
  deactivate
  die "$1"
}


# Get Python major and minor version.
#
# Optionally receives the python executable (defaults to "python").
#
get_python_ver() {
  local pyexe="${1:-python}"

  $pyexe -c 'import sys; print("%d.%d" % (sys.version_info.major, sys.version_info.minor))'
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
  local coverage

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

  if [[ $(get_python_ver) == "3.2" ]]; then
    # Coverage 4.0 dropped support for Python 3.2 (see travis-ci/travis-ci#4866)
    coverage="coverage<4.0.0.a0"
  else
    coverage="coverage"
  fi

  for i in pytest $coverage pytest-cov $codacy_deps .; do
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

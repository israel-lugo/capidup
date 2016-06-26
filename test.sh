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

  venv=$(mktemp -d --tmpdir capidup-venv-XXXXXX) || die "unable to create temp directory"

  virtualenv --python="$python_exe" "$venv"
  source "$venv/bin/activate"

  for i in pytest .; do
    pip install "$i" || unvenv_die "unable to install $i inside virtualenv"
  done

  py.test capidup
  status=$?

  deactivate

  rm -rf "$venv"

  return $status
}

test_python "python2"
test_python "python3"

#! /bin/bash


die() {
  echo "$1" >&2
  exit 1
}

unvenv_die() {
  deactivate
  die "$1"
}

venv=$(mktemp -d --tmpdir capidup-venv-XXXXXX) || die "unable to create temp directory"

virtualenv "$venv"
source "$venv/bin/activate"

for i in pytest .; do
  pip install "$i" || unvenv_die "unable to install $i inside virtualenv"
done

py.test capidup

deactivate

rm -rf "$venv"

#!/bin/bash

#
# Log <type> <msg>
#

log() {
  printf "\033[36m%s\033[0m : \033[90m%s\033[0m\n" $1 $2
}

#
# Exit with the given <msg ...>
#

abort() {
  printf "\n\033[31mError: $@\033[0m\n\n" && exit 1
}


echo
log "Convert" "README.md -> README.rst"

# convert README.md to README.rst
pandoc --from=markdown --to=rst --output=README.rst README.md || abort "fails to convert README.md"


log "Publishing.."

python setup.py sdist upload -r pypi || abort "fails to publish to PyPI"

#!/bin/bash
set -e

# which language; default py for python
lang=${1-py}

if [ "$lang" != 'py' ] && [ "$lang" != 'r' ]; then
    echo "Please pass 'py' or 'r'. You specified '$1'."
    exit 1
fi

# clean existing submission
if [ -f submission/submission.zip ]; then
    read -p "submission/submission.zip exists already. Remove? [y/n] : " yn
    case $yn in
        [Yy]* ) rm submission/submission.zip;;
        [Nn]* ) echo "... not continuing submission prep."; exit;;
        * ) echo "Please answer y or n.";;
    esac
fi

# prepare submission
cd benchmark/inference-$lang/; zip -r ../../submission/submission.zip ./*; cd ../..
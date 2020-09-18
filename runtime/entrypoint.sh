#!/bin/bash

processor="gpu"
exit_code=0

{
    cd /codeexecution

    # Check for gpu with nvidia-smi
    if [ $(which nvidia-smi) ]
    then
        :
    else
        echo "GPU unavailable; falling back to CPU."
        processor="cpu"
    fi

    echo "Unpacking submission..."
    unzip ./submission/submission.zip -d ./

    if [ -f "main.py" ]
    then
        source activate py-$processor
        echo "Running submission with Python"
        python main.py
    elif [ -f "main.R" ]
    then
	source activate r-$processor
	echo "Running submission with R"
    elif [ -f "main" ]
    then
	echo "Running submission binary"
	main
    else
        echo "ERROR: Could not find main.py, main.R, or executable main in submission.zip"
        exit_code=1
    fi

    echo "Exporting submission.csv result..."

    # Valid scripts must create a "submission.csv" file within the same directory as main
    if [ -f "submission.csv" ]
    then
        echo "Script completed its run."
        cp submission.csv ./submission/submission.csv
    else
        echo "ERROR: Script did not produce a submission.csv file in the main directory."
        exit_code=1
    fi

    echo "================ END ================"
} |& tee "/codeexecution/submission/log.txt"

# copy for additional log uses
cp /codeexecution/submission/log.txt /tmp/log
exit $exit_code

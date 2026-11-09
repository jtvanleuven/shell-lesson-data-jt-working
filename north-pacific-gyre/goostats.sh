#!/bin/bash
# goostats.sh: a research script by Nelle Nemo
# Analyze "goo" input data and write "stats" to result file.

# check for the right number of input arguments
if [ $# -ne 2 ]
then
    echo "call goostats with two arguments:" >&2
    echo "  $0 input_file result_file" >&2
    exit 1
fi

# check if files already exist (good for $1, bad for $2)
if [ ! -e "$1" ]
then
    echo "error reading input: file $1 does not exist" >&2
    exit 2
elif [ -e "$2" ]
then
    echo "error writing result: file $2 already exists" >&2
    exit 2
fi

# run the numbers
sleep 2
head -n 3 "$1" | cut -d , -f 1 | sort | uniq > "$2"

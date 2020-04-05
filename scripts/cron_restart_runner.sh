#!/usr/bin/env bash

# Check for the running `python runner` process
proc_count=`ps x | grep -c "python runner"`

# If the line count here is not 2, process
if [[ ${proc_count} -ne 2 ]]
then
    echo "Restarting runner.py:     $(date)" >> /var/log/qseek.log
    pushd ${QSEEK_ROOT}
    source .env
    echo "pwd: $(pwd)" >> /var/log/qseek.log
    ${PYTHON_EXE} scripts/text_extractor.py imperative_tweets.json
    echo "Ran text extractor" >> /var/log/qseek.log
    rm imperative_tweets.json
    nohup ${PYTHON_EXE} runner.py &>/dev/null &
        # Check again for a successful start
        if [[ ${proc_count} -ne 2 ]]
        then
            echo "Restarted runner.py successfully." >> /var/log/qseek.log
        else
            echo "Could not restart runner.py." >> /var/log/qseek.log
        fi
    popd
else
# Otherwise, do nothing
    echo "Process still running. No action.     $(date)" >> /var/log/qseek.log
fi

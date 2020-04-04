#!/usr/bin/env bash

# Check for the running `python runner` process
proc_count=`ps x | grep -c "python runner"`

# If the line count here is not 2, process
if [[ ${proc_count} -ne 2 ]]
then
    echo "Restarting runner.py:     $(date)" >> /var/log/qseek.log
    source activate qseek_env
    pushd /root/question_seeker
    python scripts/text_extractor.py imperative_tweets.json
    rm imperative_tweets.json
    nohup python runner.py &>/dev/null &
    popd
else
# Otherwise, do nothing
    echo "Process still running. No action.     $(date)" >> /var/log/qseek.log
fi

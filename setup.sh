#!/usr/bin/env bash

PROJECT_NAME="tweetpipe"

# Get the current dir.
if [ -n "$BASH_VERSION" ]; then
    TP_BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ -n "$ZSH_VERSION" ]; then
    TP_BASE_DIR=${0:a:h}  # https://unix.stackexchange.com/a/115431
else
	echo "Error: Unknown shell; cannot determine path to local repository"
fi
export TP_DIR="$TP_BASE_DIR/tweetpipe"


TP_DOCKER_BASH_HISTORY="$TP_BASE_DIR/data/docker.bash_history"
touch $TP_DOCKER_BASH_HISTORY
TP_BASE_VOLUMES="-v \"$TP_DIR:/app/tweetpipe/tweetpipe\" -v \"$TP_BASE_DIR/logs:/app/tweetpipe/logs\"" -v \"$TP_BASE_DIR/data:/app/tweetpipe/data\""
TP_IMAGE="jimfawkes/tweetpipe"
TP_ENV_FILE="--env-file $TP_DIR/config/.env"

# Convenient aliases
alias current_env="echo \"$PROJECT_NAME\""
alias cdbase="cd $TP_BASE_DIR/"

alias $PROJECT_NAME="docker run -it \
        $TP_BASE_VOLUMES \
        -v "$TP_DOCKER_BASH_HISTORY:/root/.bash_history" \
        $TP_ENV_FILE \
        --rm \
        $TP_IMAGE:latest\
"

DEV_ALIAS_NAME="$PROJECT_NAME"_dev
alias $DEV_ALIAS_NAME="docker run -it \
        $TP_BASE_VOLUMES \
        -v "$TP_DOCKER_BASH_HISTORY:/root/.bash_history" \
        $TP_ENV_FILE \
        --rm \
        $TP_IMAGE:dev\
"

BASH_ALIAS_NAME="$PROJECT_NAME"_bash
alias $BASH_ALIAS_NAME="docker run -it \
        $TP_BASE_VOLUMES \
        -v "$TP_DOCKER_BASH_HISTORY:/root/.bash_history" \
        $TP_ENV_FILE \
        --entrypoint bash \
        --rm \
        $TP_IMAGE\
"
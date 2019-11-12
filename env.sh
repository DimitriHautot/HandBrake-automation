#!/usr/bin/env bash

if [ "$HOSTNAME" == "tv-mini-box.demitripp.is-a-geek.net" ]; then
	REMOTE_BASE=/Volumes/teenanas/video-a-trier/2-to_compress
	LOCAL_BASE=/Users/Dimitri/Movies/transcode-workflow
	EXECUTABLE=~/bin/HandBrakeCLI
fi

if [ "$HOSTNAME" == "black-pc" ]; then
	REMOTE_BASE=/mnt/teenanas/video-a-trier/2-to_compress
	LOCAL_BASE=/home/dimitri/Vidéos/transcode-workflow
	EXECUTABLE=/usr/bin/HandBrakeCLI
fi

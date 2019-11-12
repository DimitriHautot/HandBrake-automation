#!/usr/bin/env bash

source ./env.sh

REMOTE_INBOX=$REMOTE_BASE/1-inbox
REMOTE_WIP=$REMOTE_BASE/2-in_progress
REMOTE_DONE=$REMOTE_BASE/3-done
REMOTE_DONE_ORIG=$REMOTE_DONE/orig

LOCAL_INBOX=$LOCAL_BASE/1-inbox
LOCAL_WIP=$LOCAL_BASE/2-in_progress
LOCAL_WIP_OUT=$LOCAL_WIP/out
LOCAL_DONE=$LOCAL_BASE/3-done
LOCAL_DONE_ORIG=$LOCAL_DONE/orig

if [ ! -d "$LOCAL_BASE" ]; then mkdir "$LOCAL_BASE"; fi
if [ ! -d "$LOCAL_INBOX" ]; then mkdir "$LOCAL_INBOX"; fi
if [ ! -d "$LOCAL_WIP" ]; then mkdir "$LOCAL_WIP"; fi
if [ ! -d "$LOCAL_WIP_OUT" ]; then mkdir "$LOCAL_WIP_OUT"; fi
if [ ! -d "$LOCAL_DONE" ]; then mkdir "$LOCAL_DONE"; fi
if [ ! -d "$LOCAL_DONE_ORIG" ]; then mkdir "$LOCAL_DONE_ORIG"; fi

# Check input parameters
if [ "$#" -lt 1 ]; then
	echo "Source media must be provided as 1st parameter (relative or absolute)"
	exit 1
fi

if [ -f "$1" ]; then
	SOURCE="$1"
	SOURCE_TYPE=local
elif [ -f "$REMOTE_INBOX/$1" ]; then
	SOURCE="$REMOTE_INBOX/$1"
	SOURCE_TYPE=remote
else
	echo "Source media could not be found. Tried with:"
	echo "*  $1"
	echo "*  $REMOTE_INBOX/$1"
	exit 2
fi
filename=$(basename "$SOURCE")

SETTINGS="--inline-parameter-sets --subtitle-lang-list fre --all-subtitles"
OUTPUT_EXT=mp4

PRESET="Capture VooCorder"
PRESET_FILE=presets/"$PRESET".json

if [ $SOURCE_TYPE == "remote" ]; then
	# 1. Move source to WIP remote directory
	mv "$SOURCE" $REMOTE_WIP

	# 2. Copy source to local input directory
	cp $REMOTE_WIP/"$filename" $LOCAL_INBOX/
fi

# 3. Move source to local work directory
INPUT=$LOCAL_WIP/"$filename"
mv $LOCAL_INBOX/"$filename" "$INPUT"

# 4. Transcode to local result directory
extension=${filename##*.}
filename_only=${filename%.*}
output_filename="$filename_only.$OUTPUT_EXT"
OUTPUT="$LOCAL_WIP_OUT"/"$output_filename"

$EXECUTABLE $SETTINGS --preset-import-file "$PRESET_FILE" --preset "$PRESET" -i "$INPUT" -o "$OUTPUT"

TRANSCODING_RESULT=$?
if [ $TRANSCODING_RESULT -ne 0 ]; then
	echo "An error occured; check the logs."
	echo "Not performing any additional file operation."
	exit 3
fi

# Move result to Done directory
mv "$OUTPUT" $LOCAL_DONE/
# Move source to Done/original local directory
mv "$INPUT" $LOCAL_DONE_ORIG/

if [ $SOURCE_TYPE == "remote" ]; then
	# Move result to remote result directory
	mv $LOCAL_DONE/"$output_filename" $REMOTE_DONE/ 2>/dev/null
	# Move source from WIP remote directory to Done/original remote directory
	mv $REMOTE_WIP/"$filename" $REMOTE_DONE_ORIG/
	# Delete original source file
	rm $LOCAL_DONE_ORIG/"$filename"

	echo "Transcoded file successfully moved to $REMOTE_DONE"
	ls -lRG $REMOTE_DONE
elif [ $SOURCE_TYPE == "local" ]; then
	echo "Input file ($SOURCE) transcoded successfully and moved to $LOCAL_DONE_ORIG"
	echo "Transcoded file available here: $LOCAL_DONE/$output_filename"
	ls -lRG $LOCAL_DONE
fi

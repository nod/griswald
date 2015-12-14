#!/bin/sh

for i in songs/* ; do
  if [ -d $i ] ; then
	python player/player.py $i/song.wav $i/song.json
  fi
done


#!/usr/bin/env python

from math import floor
import json
import sys
import time

import pygame
import RPi.GPIO as gpio

outpins = (29, 37, 35, 33, 31, 36, 38, 40)


class Performance(object):
    # singleton do __new__ and instance stuff

    def __init__(self, wav_path, channels, beats_per_sec=4):
        if len(channels) > len(outpins):
            raise Exception('Too many channels for light pins')
        self.channels = channels
        self.wav_path = wav_path
        self.init()
        self.cadence = beats_per_sec# do not hardcode
        self.keep_going = True

    @classmethod
    def reset(cls, state=0):
        for i in outpins:
            gpio.output(i, state) # all off

    @classmethod
    def init_pins(cls):
        gpio.setmode(gpio.BOARD)
        for i in outpins:
            gpio.setup(i, gpio.OUT) # all output

    def init(self):
        self.init_pins()
        self.reset(0)
        pygame.mixer.init(48000, -16, 1, 1024)
        pygame.mixer.music.load(self.wav_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.rewind()

    def start(self):
        pygame.mixer.music.play()
        self._loop()

    def _loop(self):
        print "playing:", self.wav_path
        beat = 1000 / self.cadence
        beat_adj = beat / 1000.0
        sleep_time = beat / 3.0 / 1000 # wake up every so often
        start_time = 0 # want to hit this the first time through
        chans = self.channels
        num_of_chans = len(chans)
        while self.keep_going and pygame.mixer.music.get_busy() == True:
            now = time.time()
            if now - start_time >= beat_adj:
                # slept long enough, set our lights
                start_time = now
                pos = pygame.mixer.music.get_pos()
                bucket = int(floor(pos / beat))
                i = 0
                while i < num_of_chans:
                    gpio.output(outpins[i], chans[i][bucket])
                    i+=1
            time.sleep(sleep_time)
        print "song done"
        self.reset(0) # leave them "off"
        time.sleep(sleep_time * 3)
        self.reset(1) # leave them "on"


if __name__ == '__main__':
    
    wav = sys.argv[1]
    js = sys.argv[2]
    dat = json.loads(open(js).read())
    Performance(
        wav,
        dat['channels'],
        beats_per_sec=dat.get('beats_per_sec', 4) ).start()


#!/usr/bin/env python

import json
import sys
import wave

"""
totally naive i don't know squat about wav files way of creating binning type
sequences for a wav file
"""


def get_wave_data(wav, slots_per_sec=4):
    w = wave.open(wav)
    frate = w.getframerate()
    nframes = w.getnframes()
    print >>sys.stderr, "NFRAMES:", nframes
    print >>sys.stderr, "FRATE:", frate
    frames = [ord(i) for i in w.readframes(-1)]
    bucketsize = frate/slots_per_sec
    print >>sys.stderr, "BUCKETSIZE:", bucketsize
    data = []
    for i in xrange(0,nframes, bucketsize):
        data.append( int(sum(frames[i:i+bucketsize])/float(bucketsize)) )
    print >>sys.stderr, "LENDATA", len(data)
    return data

def seq_cliff(d, cliff=127):
    return [ (1 if i>cliff else 0) for i in d ]

def avg(d):
    return int(sum(d) / float(len(d)))

def seq_time_travel(d, before=8, after=2):
    ret = []
    for i in xrange(len(d)):
        s_ = i - before
        s_idx = s_ if s_ > 0 else 0
        sample = d[s_idx:s_idx+after]
        if d[i] > avg(sample):
            ret.append(1)
        else:
            ret.append(0)
    return ret


def gen_sequences(wav_data, num=4):
    #  prefix=8  suffix=5
    # int channel_size = {size} + 8 + 5;
    sequences = [
        lambda d: seq_time_travel(d, 6, 10),
        lambda d: seq_time_travel(d),
        lambda d: seq_time_travel(d, 16, 5),
        lambda d: seq_time_travel(d, 4, 4),
        lambda d: seq_cliff(d),
        lambda d: seq_time_travel(d, 30, 4),
        lambda d: seq_time_travel(d, 2, 10)
    ]

    return [ x(wav_data) for x in sequences[:num] ]


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        raise SystemExit('usage: seqr IN_WAVE_FILE [OUTPUTFILE or stdout]')
    wav = sys.argv[1]
    if len(sys.argv) == 3:
        outf = open(sys.argv[2], 'w')
    else:
        outf = sys.stdout
    beats_sec = 4
    d = get_wave_data(wav, slots_per_sec=beats_sec)
    seqs = gen_sequences(d,8)

    outf.write(json.dumps(
        dict(channels=seqs, wavname=wav, beats_per_sec=beats_sec),
        indent=2 ))

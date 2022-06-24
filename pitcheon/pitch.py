import io
import math
import re

import crepe
import numpy as np
import scipy
import wquantiles

from . import util

def smpl_pitch_to_note(unity_note, pitch_fraction):
  return unity_note + pitch_fraction/0x80000000*0.5

def note_to_smpl_pitch(note):
  return math.floor(note), round((note % 1) * 0x80000000 * 2)

def note_to_freq(note):
  ref_note = 69
  ref_freq = 440.0
  return ref_freq * 2**((note - ref_note)/12)

def freq_to_note(freq):
  ref_freq = 440.0
  ref_note = 69
  return math.log(freq / ref_freq, 2) * 12 + ref_note

class NotePitch:
  RE = re.compile(r"^([ABCDEFG])([#b]?)(-?\d+)(?:(\+|-)(\d+))?$", re.IGNORECASE)
  BASE_NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
  MODIFIERS = {"": 0, "#": 1, "b": -1}
  CENT_SIGNS = {"+": 1, "-": -1, None: 0}

  def __init__(self, note):
    self._note = note
  
  @classmethod
  def parse(cls, s):
    m = cls.RE.match(s)
    if not m:
      raise ValueError("invalid note pitch")
    base_note = cls.BASE_NOTES[m.group(1).upper()]
    modifier = cls.MODIFIERS[m.group(2)]
    octave = int(m.group(3))
    cent_sign = cls.CENT_SIGNS[m.group(4)]
    cents = int(m.group(5)) if m.group(5) is not None else 0
    return cls(base_note + modifier + (octave+1)*12 + cent_sign * cents * 0.01)

  def note(self):
    return self._note

  def smpl_pitch(self):
    return note_to_smpl_pitch(self._note)

  def freq(self):
    return note_to_freq(self._note)
    
class HertzPitch:
  RE = re.compile(r"^((?:\d*\.)?\d+)Hz$", re.IGNORECASE)

  def __init__(self, freq):
    self._freq = freq

  @classmethod
  def parse(cls, s):
    m = cls.RE.match(s)
    if not m:
      raise ValueError("invalid Hertz pitch")
    return cls(float(m.group(1)))
    
  def note(self):
    return freq_to_note(self._freq)

  def smpl_pitch(self):
    return note_to_smpl_pitch(self.note())

  def freq(self):
    return self._freq

class SmplPitch:
  RE = re.compile(r"^(\d+)(?:,(\d+))$")

  def __init__(self, note, frac):
    self._smpl_pitch = (note, frac)

  @classmethod
  def parse(cls, s):
    m = cls.RE.match(s)
    if not m:
      raise ValueError("invalid smpl pitch")
    return cls(int(m.group(1)), int(m.group(2)))
    
  def note(self):
    return smpl_pitch_to_note(*self._smpl_pitch)

  def smpl_pitch(self):
    return self._smpl_pitch

  def freq(self):
    return note_to_freq(self.note())

class CrepePitch:
  RE = re.compile(r"^crepe$", re.IGNORECASE)

  def __init__(self, freq=None):
    self._freq = freq

  @classmethod
  def parse(cls, s):
    if not cls.RE.match(s):
      raise ValueError("invalid crepe pitch")
    return cls()
    
  def detect(self, audio, sr):
    time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
    a = np.column_stack((time, frequency, confidence))
    # f = io.StringIO()
    # np.savetxt(
    #   f, a,
    #   ['%.3f', '%.3f', '%.6f'],
    #   header='time,frequency,confidence',delimiter=','
    # )
    # table = f.getvalue()
    # print()
    # print(table)
    note = np.vectorize(freq_to_note)(frequency)
    wmedian_note = wquantiles.median(note, confidence)
    self._freq = note_to_freq(wmedian_note)
    
  def note(self):
    return freq_to_note(self._freq)

  def smpl_pitch(self):
    return note_to_smpl_pitch(self.note())

  def freq(self):
    return self._freq

def pitchtype(s):
  for cls in (NotePitch, HertzPitch, SmplPitch, CrepePitch):
    try:
      return cls.parse(s)
    except:
      pass
  raise ValueError("invalid pitchtype")

def note_str(pitch):
  return f"{pitch.note():.3f}"

def smpl_str(pitch):
  note, frac = pitch.smpl_pitch()
  return f"({note}, {frac})"

def freq_str(pitch):
  return f"{pitch.freq():.3f}Hz"

def mega_str(pitch):
  return f"note: {note_str(pitch)} / freq: {freq_str(pitch)} / smpl: {smpl_str(pitch)}"

import argparse
import math
import os
import struct
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
from scipy.io import wavfile
from wave_chunk_parser.chunks import RiffChunk, GenericChunk

from samplechunker import pitch
from samplechunker import util

def print_err(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

class SmplChunk:
  STRUCT = struct.Struct("<4s4sIIIIIII")
  
  def __init__(self, manufacturer=b"\x00\x00\x00\x00", product=b"\x00\x00\x00\x00", sample_period=0x00005893, midi_unity_note=60, midi_pitch_fraction=0, smpte_format=0, smpte_offset=0, num_sample_loops=0, sample_data=0, rest=np.array((), dtype=np.uint8)):
    self.manufacturer = manufacturer
    self.product = product
    self.sample_period = sample_period
    self.midi_unity_note = midi_unity_note
    self.midi_pitch_fraction = midi_pitch_fraction
    self.smpte_format = smpte_format
    self.smpte_offset = smpte_offset
    self.num_sample_loops = num_sample_loops
    self.sample_data = sample_data
    self.rest = rest

  @classmethod
  def parse(cls, data):
    struct_len = cls.STRUCT.size
    return cls(*cls.STRUCT.unpack(data[:struct_len]), rest=data[struct_len:])
    
  def to_bytes(self):
    struct_bytes = self.STRUCT.pack(
      self.manufacturer, self.product, self.sample_period,
      self.midi_unity_note, self.midi_pitch_fraction, self.smpte_format, self.smpte_offset,
      self.num_sample_loops, self.sample_data
    )
    try:
      return np.append(np.frombuffer(struct_bytes, dtype=np.uint8), self.rest)
    except Exception as e:
      print(e)
      import pdb; pdb.set_trace()

def process_path(path, args):
  if os.path.isdir(path):
    for fn in os.listdir(path):
      process_path(os.path.join(path, fn), args)
    return

  if not path.lower().endswith(".wav"):
    return

  print_err()
  print_err(path)
  
  with open(path, "rb") as file:
    riff_chunk = RiffChunk.from_file(file)

  smpl_chunks = riff_chunk.get_chunks("smpl")
  num_smpl = len(smpl_chunks)
  
  print_err(f"  {num_smpl} smpl chunk(s)")

  smpl_chunk = None
  for i, smpl_chunk_generic in enumerate(smpl_chunks):
    data = smpl_chunk_generic.datas
    smpl_chunk = SmplChunk.parse(data)
    smpl_pitch = pitch.SmplPitch(smpl_chunk.midi_unity_note, smpl_chunk.midi_pitch_fraction)
    print_err(f"    [{i}] {pitch.mega_str(smpl_pitch)}")

  if smpl_chunk is None:
    smpl_chunk = SmplChunk()
    
  if args.pitch is None:
    return
    
  if hasattr(args.pitch, "detect"):
    print_err("  detect pitch...")
    with util.suppress_stderr():
      with util.suppress_stdout():
        sr, audio = wavfile.read(path)
        args.pitch.detect(audio, sr)
  else:
    print_err("  specified pitch")

  print_err(f"    {pitch.mega_str(args.pitch)}")
  smpl_pitch = args.pitch.smpl_pitch()
  smpl_chunk.midi_unity_note, smpl_chunk.midi_pitch_fraction = smpl_pitch

  has_existing_smpl = num_smpl > 0
  if has_existing_smpl and not args.overwrite:
    print_err(f"  don't write (smpl chunk exists)")
    return

  new_chunks = []
  smpl_generic_chunk = GenericChunk(b"smpl", smpl_chunk.to_bytes())
  smpl_added = False
  for chunk in riff_chunk.sub_chunks:
    name = chunk.get_name
    if name == b"smpl":
      if smpl_added:
        continue
      new_chunks.append(smpl_generic_chunk)
      smpl_added = True
    else:
      new_chunks.append(chunk)

  if not smpl_added:
    new_chunks.append(smpl_generic_chunk)
      
  new_riff_chunk = RiffChunk(new_chunks)
  
  write_path = path

  if args.dry:
    print_err(f"  would write {write_path}")
    return
  
  print_err(f"  write {write_path}")
  with open(write_path, "wb") as wf:
    wf.write(new_riff_chunk.to_bytes())

def main():
  parser = argparse.ArgumentParser(
    description="tag WAV files with pitch metadata."
  )
  parser.add_argument(
    "-p", "--pitch", type=pitch.pitchtype, default=None,
    help="the pitch; valid values are 12-TET notes +/- cents (e.g. 'C3', 'A#4', 'Db2+25'), absolute frequencies (e.g. '654.32Hz'), raw MIDI unity note / pitch fraction pairs (e.g. '60,134217728'), or 'crepe' (automatic pitch detection)"
  )
  parser.add_argument(
    "path",
    help="file or directory to process. if a directory is given, all *.wav files inside it (and subdirectories) will be processed"
  )
  parser.add_argument(
    "-d", "--dry", action="store_true", default=False,
    help="don't modify any files, just print what would be done"
  )
  parser.add_argument(
    "-o", "--overwrite", action="store_true", default=False,
    help="when a file has an existing smpl chunk, overwrite it"
  )

  args = parser.parse_args()

  process_path(args.path, args)
    
if __name__ == "__main__":
  main()

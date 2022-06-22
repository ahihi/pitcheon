import argparse
import math
import struct
import sys

from wave_chunk_parser.chunks import RiffChunk

from samplechunker import pitch

def print_err(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

class SmplChunk:
  STRUCT = struct.Struct("4s4sIIIIIII")
  
  def __init__(self, data):
    struct_len = self.STRUCT.size
    (self.manufacturer, self.product, self.sample_period, self.midi_unity_note,
     self.midi_pitch_fraction, self.smpte_format, self.smpte_offset,
     self.num_sample_loops, self.sample_data) = self.STRUCT.unpack(data[:struct_len])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--pitch", type=pitch.pitchtype, default=None)
  parser.add_argument("file")

  args = parser.parse_args()

  with open(args.file, "rb") as file:
    riff_chunk = RiffChunk.from_file(file)

  smpl_chunks = riff_chunk.get_chunks("smpl")
  num_smpl = len(smpl_chunks)
  
  print_err(f"{num_smpl} smpl chunk(s) found")

  for i, smpl_chunk_generic in enumerate(smpl_chunks):
    data = smpl_chunk_generic.datas
    smpl_chunk = SmplChunk(data)
    midi_unity_note = smpl_chunk.midi_unity_note
    midi_pitch_fraction = smpl_chunk.midi_pitch_fraction
    freq = pitch.note_to_freq(pitch.smpl_pitch_to_note(midi_unity_note, midi_pitch_fraction))
    print_err()
    print_err(f"smpl chunk {i}")
    print_err(f"  midi unity note: {midi_unity_note}")
    print_err(f"  midi pitch fraction: {smpl_chunk.midi_pitch_fraction}")
    print_err(f"  -> freq: {freq} Hz")

    if args.pitch is not None:
      print_err()
      print_err("--pitch")
      print_err(f"  note: {args.pitch.note()}")
      print_err(f"  freq: {args.pitch.freq()}")
      print_err(f"  smpl_pitch: {args.pitch.smpl_pitch()}")
    
if __name__ == "__main__":
  main()

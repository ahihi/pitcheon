# pitcheon

a utility for tagging WAV files with pitch metadata.

pitch can be specified manually or automatically detected with [CREPE](https://github.com/marl/crepe). the metadata is stored in the [`smpl` chunk](https://www.recordingblogs.com/wiki/sample-chunk-of-a-wave-file), in particular the MIDI unity note and MIDI pitch fraction fields.

## installation

### with pitch detection

in theory:

```shell
pip install .[crepe]
```

in practice... tensorflow stuff seems to work better when installed by conda:

```
conda create -n pitcheon -c conda-forge 'python>=3.7' numpy openblas 'tensorflow>=2.8,<3' 'crepe>=0.0.12'
conda activate pitcheon
pip install .[crepe]
```

### without pitch detection

```shell
pip install .
```

## usage

**THIS IS EXPERIMENTAL SOFTWARE! make sure you have backups of your WAV files.**

```shell
pitcheon --help
```

```
usage: pitcheon [-h] [-p PITCH] [-d] [-o] path

tag WAV files with pitch metadata.

positional arguments:
  path                  file or directory to process. if a directory is given, all *.wav files
                        inside it (and subdirectories) will be processed

optional arguments:
  -h, --help            show this help message and exit
  -p PITCH, --pitch PITCH
                        the pitch; valid values are 12-TET notes +/- cents (e.g. 'C3', 'A#4',
                        'Db2+25'), absolute frequencies (e.g. '654.32Hz'), raw MIDI unity note /
                        pitch fraction pairs (e.g. '60,134217728'), or 'crepe' (automatic pitch
                        detection)
  -d, --dry             don't modify any files, just print what would be done
  -o, --overwrite       when a file has an existing smpl chunk, overwrite it
```

## known issues

- CREPE produces a time series of pitch and confidence. pitcheon currently boils this down to a single pitch by computing a weighted median, but there are probably better methods.

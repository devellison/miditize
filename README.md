# miditize.py

Simple python utility script to convert images to midi files.
Generally they'll sound like a drunken goat flopping on a piano.




Major dependencies:
- pillow
- numpy
- opencv-python (cv2)
- midiutil


## Usage
```
D:\github\miditize>miditize.py -h
usage: miditize.py [-h] [-y Y] [-t T] [-g] [-s] [-r R] [-e] input_image output_midi

MIDI-tize your images!

positional arguments:
  input_image  Input image file (required)
  output_midi  Output MIDI file (required)

optional arguments:
  -h, --help   show this help message and exit
  -y Y         Y scale (0.1 is default)
  -t T         Gray Threshold (64 is default)
  -g           Channel Gradient Mode
  -s           Show resized image
  -r R         Rotation (counter-clockwise, 0=none, 1=90, 2=180, 3=270)
  -e           Edges
```

`miditize.py` first converts the image to grayscale, applies any requested rotation, 
then scales it to 128 pixels wide while keeping the existing aspect ratio.  
It will then apply any image processing (e.g. edge detection) and finally process the image - spitting out MIDI notes 
where pixel colors change.

The default mode is simply a threshold - the default is 64, but can be set via the `-t` option. 
Any pixels brighter than the threshold are considered part of a note, those less than the threshold are beautiful silence.
The "Channel Gradient" mode has a much lower threshold for silence (< 16), and anything brighter than that becomes a note. 
The channel is based off the brightness.  Threshold mode is best for line images, text, etc.  
Channel Gradient mode is best for photo-type images or cartoons.


The Y scale scales how long a note is per pixel.  I'm using the floating point interface for MIDIUtil's addNote, 
so a Y scale of 0.1 means each pixel is going to be 1/10 of a quarter note long.  
You should expect to need to play with the Y scale a bit for your specific application.


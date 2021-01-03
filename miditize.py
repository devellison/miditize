
# Miditize - converts images into MIDI

import argparse
from dataclasses import dataclass
from PIL import Image
from midiutil import MIDIFile
import numpy
import cv2
import math


# Get and check our command-line arguments
parser = argparse.ArgumentParser(description='MIDI-tize your images!')
parser.add_argument("input_image", type=str, help="Input image file (required)")
parser.add_argument("output_midi", type=str, help="Output MIDI file (required)")
parser.add_argument("-y", type=float, default=0.1, help="Y scale (0.1 default)")
parser.add_argument("-t", type=int,  default=64, help="Gray Threshold")
parser.add_argument("-g", action="store_true", help="Channel Gradient Mode")
parser.add_argument("-s", action="store_true", help="Show resized image")
parser.add_argument("-r", type=int, default=0, help="Rotation (0=none)")
parser.add_argument("-e", action="store_true", help="Edges")
args = parser.parse_args()

#_------------------------------------------------------
# Note tracking class
@dataclass
class Note:
    noteVal: int
    start: float
    velocity: int
    length: float
    channel: int
        
    def begin(self,noteVal,start,velocity,channel):
        self.noteVal = noteVal
        self.start = start
        self.velocity = int(velocity / 2) # grayscale is 0-255, velocity is 0-127
        self.length = 0
        self.channel = channel
    def end(self,endPos):
        self.length = endPos - self.start
    def reset(self):
        self.noteVal = -1
        self.start = -1
        self.velocity = 0
        self.length = 0
        self.channel = 0


# Setup a note array for tracking
NoteArray = []
for i in range(128):
    NoteArray.append(Note(-1,0,0,0,0))

# Add a note to the MIDI file
def AddNote(midiFile, theNote, yScale):
    midiFile.addNote(0,theNote.channel,
                       theNote.noteVal,
                       theNote.start * yScale, 
                       theNote.length * yScale,
                       theNote.velocity)

# Handle pixels in threshold mode
# MidiUtil wants the length for each note, so we track them
# until they end then submit.
def OnPixelThresh(midiFile, x, y, gray, yScale, threshold):
    if (gray >= threshold):
        if (NoteArray[x].noteVal == -1):
            NoteArray[x].begin(x,y,gray,0)
    else:
        if (NoteArray[x].noteVal > -1):
            NoteArray[x].end(y)
            AddNote(midiFile,NoteArray[x],yScale)
            NoteArray[x].reset()

# Handle pixels in channel gradient mode
def OnPixelGrad(midiFile, x, y, gray, yScale):
    if (gray < 16):
            if (NoteArray[x].noteVal >= 0):
                NoteArray[x].end(y)
                AddNote(midiFile,NoteArray[x],yScale)
                NoteArray[x].reset()
    else:
        newChan = math.floor(gray/16);
        if (NoteArray[x].noteVal == -1):
            NoteArray[x].begin(x,y,gray,newChan)
        else:
            if (newChan != NoteArray[x].channel):
                NoteArray[x].end(y)
                AddNote(midiFile,NoteArray[x],yScale)
                NoteArray[x].reset()
                NoteArray[x].begin(x,y,gray,newChan)


# ------------------------------------------------------------------------------------

# read image and convert it to grayscale
image = Image.open(args.input_image).convert('L')

# rescale it so width is 128 across (128 notes in MIDI)
# might apply y-scale here, but currently applying it to note length.
ratio = 128.0/image.size[0]
newSize = (128,int(image.size[1]*ratio))
image = image.resize(newSize);

# Put it into an easy array to play with.
imagePix = numpy.array(image)

# if we want just edges, use a pretty arbitrary Canny
# and convert it back for the preview
if args.e:
    edges = cv2.Canny(imagePix,150,200)
    imagePix = cv2.convertScaleAbs(edges)
    image = Image.fromarray(imagePix)
   


# Preview the image if desired
if args.s:
    image.show()

# Start our MIDI file.
mFile = MIDIFile(numTracks=1, adjust_origin=True,file_format=1)
             
# Loop through image
for y in range(newSize[1]):
    for x in range(128):
        pixel = imagePix[y,x]
        if (args.g):
            OnPixelGrad(mFile,x,y,pixel,args.y)
        else:
            OnPixelThresh(mFile,x,y,pixel,args.y,args.t)

# End any notes we had.
for x in range(128):
    if (args.g):
        OnPixelGrad(mFile,x,newSize[1],0,args.y)
    else:
        OnPixelThresh(mFile,x,newSize[1],0, args.y,args.t)

# Write out the MIDI file.
midiOut = open(args.output_midi, 'wb')
mFile.writeFile(midiOut)
mFile.close()


import os
import numpy as np
from warnings import warn
from .boardbuilder import *
from PIL import Image, ImageDraw, ImageFont

scale = {         "C": 0, "C♯": 1,
         "D♭": 1, "D": 2, "D♯": 3,
         "E♭": 3, "E": 4,
                  "F": 5, "F♯": 6,
         "G♭": 6, "G": 7, "G♯": 8,
         "A♭": 8, "A": 9, "A♯": 10,
         "B♭": 10, "B": 11,
        }

scaleInv = {value: key for key, value in scale.items()}
scaleInv = {i: scaleInv[i] for i in range(12)}

# Tuning of the uke
strings = [7, 0, 4, 9]

chords = {"": [0, 4, 7],
          "⁶": [0, 4, 7, 9],
          "⁷": [0, 4, 7, 10],
          "M⁷": [0, 4, 7, 11],
          "+": [0, 4, 8],
          "+⁷": [0, 4, 8, 10],
          "m": [0, 3, 7],
          "m⁶": [0, 3, 7, 9],
          "m⁷": [0, 3, 7, 10],
          "m/M7": [0, 3, 7, 11],
          "dim": [0, 3, 6],
          "dim⁷": [0, 3, 6, 9],
         }

def move_down_highest_finger(notes: list, positions: list) -> (int, int):
    # highest finger position, lowest step size to the next note in the chord
    highest = [i for i in range(len(strings)) if positions[i] == min(positions)]
    lowest = 12
    toMove = -1
    new = -1
    for idx in highest:
        start = strings[idx] + positions[idx] + 1
        stepSizes = [(note - start) % 12 for note in notes]
        nxtCand = stepSizes.index(min(stepSizes))
        if stepSizes[nxtCand] < lowest:
            lowest = stepSizes[nxtCand]
            new = notes[nxtCand]
            toMove = idx
    return toMove, new


# Idea: go down each string and play the first note that belongs to the chord.
# If notes are missing, move down the highest-placed finger
def find_chord(rootstr: str, kind: str, verbosity: int = 0) -> str:
    root = scale[rootstr]
    notes = [(root + step) % 12 for step in chords[kind]]
    firsts = []
    if verbosity >= 2:
        print("Searching chord", rootstr + kind, "for tuning", [scaleInv[s] for s in strings])
    for string in strings:
        first = string - 1
        for note in notes:
            if (note - string) % 12 < (first - string) % 12:
                first = note
        firsts.append(first)
    it = 0
    fingerPositions = [(firsts[i] - strings[i]) % 12 for i in range(len(strings))]
    while len(set(firsts)) != len(set(notes)) and it <= 10:
        if verbosity >= 2:
            print("Attempt", it + 2, "looking for chord", rootstr+kind)
            print("Required: ", [scaleInv[note] for note in notes], "Present: ", [scaleInv[note] for note in firsts])
        toMove, new = move_down_highest_finger(notes, fingerPositions)
        if (toMove < 0 or new < 0) and verbosity >= 0:
            warn("Uh oh, something went wront with the chord finding algorithm for", rootstr + kind)
        firsts[toMove] = new
        fingerPositions[toMove] = (firsts[toMove] - strings[toMove]) % 12
        it += 1
    for i in range(len(strings)):
        for j in range(i+1, len(strings)):
            if strings[i] == strings[j] and fingerPositions[i] == fingerPositions[j]:
                fingerPositions[i] = "x"
    if it <= 10 and verbosity >= 1:
        print("Found", fingerPositions, "/", [scaleInv[note] for note in firsts], "for chord", rootstr + kind, "\n")
    if it > 10 and verbosity >= 0:
        warn("Finger positions for chord", rootstr + kind, "could not be found")
    return ''.join([str(pos) for pos in fingerPositions])


def draw_chord(placements: str, aa: bool = False, verbosity: int = 0) -> np.ndarray:
    if len(placements) != len(strings) and verbosity >= 0:
        warn("Chord specification and number of strings don't match")
    board = draw_board()
    if(placements == "empty"):
        board[:] = 0
        return board

    full, circle, cross = (draw_mark(mark, aa, verbosity) for mark in "fox")
    for string, placement in enumerate(placements):
        if placement == 'x':
            mark = cross
            placement = 0
        elif placement == '0':
            mark = circle
            placement = 0
        else:
            mark = full
            placement = int(placement)
        board = place_mark(board, mark, string, placement)
    return board 


def label_chord(chord: np.ndarray, name: str) -> np.ndarray:
    if tabSizes["labelSize"] <= 0:
        return chord
    y, x = chord.shape

    # Handle superscript part of the chord names
    supText = ""
    supStart = min([name.find(c) if name.find(c) >= 0 else len(name) for c in "¹²³⁴⁵⁶⁷⁸⁹⁰"])
    name, supText = name[:supStart], name[supStart:] # unchanged if no superscript is found
    for idx, c in enumerate(supText):
        c = "¹²³⁴⁵⁶⁷⁸⁹⁰".find(c)
        supText = supText[:idx] + "1234567890"[c] + supText[idx + 1:]

    # Draw the label
    markSize, (padl, padt) = tabSizes["markSize"], tabSizes["padding"][0:2] # Those are the placement coordinates
    labelSize = tabSizes["labelSize"]
    txt = Image.new("L", (x, labelSize), 255)
    fntpath = os.path.dirname(__file__) + "/../font/mononoki-Bold-with-music.ttf"
    fnt = ImageFont.truetype(fntpath, size = (labelSize * 4) // 5)
    supFnt = ImageFont.truetype(fntpath, size = (labelSize * 3) // 5)
    draw = ImageDraw.Draw(txt)
    draw.text((markSize // 2 + padl, 0), name, font = fnt)
    draw.text((markSize // 2 + padl + draw.textsize(name, font = fnt)[0], 0), supText, font = supFnt)
    txt = np.array(txt)
    res = np.ones((y + txt.shape[0], x)) * 255
    res[padt: padt + labelSize], res[padt + labelSize:] = txt, chord[padt:]

    return res

def build_chord(note: str, kind: str, aa: bool = False, verbosity: int = 0) -> np.ndarray:
    chord = find_chord(note, kind, verbosity)
    chord = draw_chord(chord, aa, verbosity)
    chord = label_chord(chord, note+kind)
    return chord

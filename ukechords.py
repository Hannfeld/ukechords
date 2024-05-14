#!/usr/bin/python3
from PIL import Image
import numpy as np
from util.chordbuilder import *
from util.sheetbuilder import *


if __name__ == "__main__":
    rows = [] # the chords to be printed, sorted into rows

    # scaleInv decodes the base notes from their integer represantation
    scl = [scaleInv[note] for note in range(12)] 

    # all implemented chord types are in the "chords" dict in chordbuilder.py
    kinds = ["", "⁷", "M⁷", "m", "m⁷", "⁶"] 

    # background and foreground color, default is white (1, 1, 1) and black (0, 0, 0)
    bg, fg = (1, 1, .9), (.2, .25, .3)

    # fill "rows" with rows of chords, in this (and probably most) cases each base note has a row
    for note in scl:
        row = []
        for chord in kinds:
            # build_chord determines appropiate finger positions from the chord name,
            # then draws the board
            row.append(build_chord(note, chord, aa = True))
        rows.append(row)

    # this function essentially flips the sheet diagonally for 2+ metacolumns.
    # metacolums are the number of rows (as defined in the "rows" variable) placed horizontally.
    # in this example, it makes it so that the base notes ascend left to right first, then down
    mcols = 2
    rows = flip(rows, mcols)

    # finally, assemble the sheet. can return an image or a numpy array
    sheet = build_sheet(rows, metacols = mcols, bgcolor = bg, fgcolor = fg, asImage = True)
        
    sheet.show()
    sheet.save("example/chord-cheat-sheet.jpg", quality = 100)


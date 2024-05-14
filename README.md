# Ukechords
Simple python program for generating ukulele (and other string instruments) chord cheat sheets. Supports variable string counts, different tunings, simple colorization and a bunch of layout parameters.

# Usage

Getting an image for a specific ukulele chord is as simple as:

```python
import ukechords as uc
from PIL import Image

chord = uc.build_chord("B♭", "m")
chord = Image.fromarray(chord)
chord.show()
```


Building a whole sheet is slightly more involved. Here's a complete, working example:

```python
import ukechords as uc

# not used in this example, but the settings for the fret board can be found and edited in the uc.tabSizes dict
# the settings for the sheet assembly can be found and edited in the uc.sheetSizes dict

# uc.scale encodes the base notes into their integer representation
# uc.scaleInv decodes the base notes from their integer represantation
scl = [uc.scaleInv[note] for note in range(12)] 

# all implemented chord types are saved - and can be expanded upon - in the uc.chords dict
types = ["", "⁷", "M⁷", "m", "m⁷", "⁶"] 

# background and foreground color, default is white (1, 1, 1) and black (0, 0, 0)
# in this case, a slight yellowish tint and a dark blue
bg, fg = (1, 1, .9), (.2, .25, .3)

# fill "rows" with rows of chords, in this (and probably most) cases each base note has a row
rows = []
for note in scl:
    row = []
    for typ in types:
        if True:
            # build_chord determines appropiate finger positions from the chord name,
            # then draws the board
            row.append(uc.build_chord(note, typ, aa = True))
        else:
            # alternatively, do it by hand:
            chord = uc.find_chord(note, typ)            # gives the finger placements for the chord as a string
            chord = uc.draw_chord(chord, aa = True)     # can also draw custom chords, returns a numpy array
            chord = uc.label_chord(chord, note + typ)   # adds the label - required if combined with auto-generated chords! (or set label size to 0)
            row.append(chord)
    rows.append(row)

# this function essentially flips the sheet diagonally for 2+ metacolumns.
# metacolums are the number of rows (as defined in the "rows" variable) placed horizontally.
# in this example, it makes it so that the base notes ascend left to right first, then down
mcols = 2
rows = uc.flip(rows, mcols)

# finally, assemble the sheet and return it as an PIL Image (default) or a numpy array
sheet = uc.build_sheet(rows, metacols = mcols, bgcolor = bg, fgcolor = fg, asImage = True)
    
sheet.show()
sheet.save("chord-cheat-sheet.jpg", quality = 100)
```

The result looks like this:

<img src="/example/chord-cheat-sheet.jpg" width=50%>

Another example that requires a bit of tinkering with the settings:

<img src="/example/chord-cheat-sheet-big.jpg" width=50%>

Although that isn't the focus of this software, it can also be generalized to other tunings or even other instruments. For example, the following two lines are all that's needed to use ukechords for a guitar:

```python
uc.strings[:] = [4, 9, 2, 7, 11, 4] # integer representations of E-A-D-G-B-E tuning
uc.tabSizes["nStrings"] = 6
```

Both the chord generation (although it doesn't always find the best pattern) and the chord visualization (without issues) work for guitars as well.

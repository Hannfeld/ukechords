import numpy as np
from PIL import Image
import math
from .boardbuilder import *

sheetSizes = {"padding": [10, 10, 10, 10], # left, top, bottom, right
              "separatorWidth": 4, "separatorIntensity": .8,
             }

def pad_and_get_dims(rows: list[list[np.ndarray]], mcols: int) -> (int, int, list[list[np.ndarray]]):
    if len(rows) % mcols > 0:
        toPad = mcols - (len(rows) % mcols)
        for i in range(toPad):
            rows.append([])
    nrows = len(rows)
    ncols = max([len(row) for row in rows])
    for row in rows:
        for i in range(ncols - len(row)):
            row.append(spacer())
    return (nrows, ncols, rows)


def build_sheet(rows: list[list[np.ndarray]], metacols: int = 1, 
                bgcolor: (float, float, float) = (0, 0, 0), fgcolor: (float, float, float) = (255, 255, 255), 
                asImage: bool = True, verbosity: int = 0
                ) -> np.ndarray | Image.Image:
    if tabSizes["markSize"] > tabSizes["fretDist"] and verbosity >= 0:
        warn("Size of Marks larger than the fret gaps to place them on")
    (padl, padt, padb, padr) = sheetSizes["padding"]
    sepWidth, sepIntens = sheetSizes["separatorWidth"], sheetSizes["separatorIntensity"]

    # assemble chords on sheet
    y, x = rows[0][0].shape
    nrows, ncols, rows = pad_and_get_dims(rows, metacols)
    
    maxrows = math.ceil(nrows / metacols)
    height = padt + padb + maxrows * y
    mColWidth = ncols * x + sepWidth
    res = np.full((height, padl), 255)
    currx = padl
    curry = padt
    for r in range(nrows):
        curry = padt + (r % maxrows) * y
        if r % maxrows == 0:
            if r > 0:
                res = np.c_[res, np.full((height, sepWidth), 255) * sepIntens]
            res = np.c_[res, np.full((height, ncols * x), 255)]
        for c in range(ncols):
            currx = padl + c * x + (r // maxrows) * mColWidth
            res[curry: curry + y, currx: currx + x] = rows[r][c] 
    res = np.c_[res, np.full((height, padr), 255)]
    
    res = np.stack([res, res, res], axis = 2) # greyscale -> rgb

    # color it
    bgcolor = (np.minimum(np.maximum(0, bgcolor), 1))
    fgcolor = (np.minimum(np.maximum(0, fgcolor), 1))
    for i in range(3):
        color = res[:,:,i]
        if bgcolor[i] < fgcolor[i]:
            color = np.full(color.shape, 255) - color
        bg, fg = min(fgcolor[i], bgcolor[i]), max(fgcolor[i], bgcolor[i])
        color /= 255
        color *= (fg - bg)
        color += bg
        color *= 255
        color = np.maximum(0, color)
        color = np.minimum(255, color)
        res[:,:,i] = color
    
    res = res.astype(np.uint8)
    if asImage:
        res = Image.fromarray(res)

    return res


def flip(rows: np.ndarray, mcols: int) -> np.ndarray:
    nrows, ncols, rows = pad_and_get_dims(rows, mcols)
    
    res = rows.copy()
    for i in range(0, (len(rows) - 1) * mcols, mcols):
        res[i//mcols] = rows[i % (len(rows) - 1)]
    return res

import numpy as np
from warnings import warn

tabSizes = {
        "markSize": 15, "markLineWidth": 2, "labelSize": 30,
        "padding": [20, 20, 20, 20], # left, top, bottom, right
        "nFrets": 7, "fretLineWidth": 4, "topLineWidth": 6, "bottomLineWidth": 0, "fretDist": 24,
        "nStrings": 4, "stringLineWidth": 2, "stringDist": 22,
        }

def get_board_size(label: bool = True) -> (int, int):
    padl, padt, padb, padr = tabSizes["padding"]
    markSize, labelSize = tabSizes["markSize"], tabSizes["labelSize"]
    nFrets, fretWidth, topWidth, bottomWidth, fretDist = tabSizes["nFrets"], tabSizes["fretLineWidth"], tabSizes["topLineWidth"], tabSizes["bottomLineWidth"], tabSizes["fretDist"] 
    nStrings, stringWidth, stringDist = tabSizes["nStrings"], tabSizes["stringLineWidth"], tabSizes["stringDist"]
    x = markSize + padl + padr + nStrings * stringWidth + (nStrings - 1) * stringDist
    y = markSize + padt + padb + (nFrets - 2) * fretWidth + (nFrets - 1) * fretDist + topWidth + bottomWidth
    if label:
        y += labelSize
    return x, y


def draw_mark(symbol: chr = 'f', aa: bool = False, verbosity: int = 0) -> np.ndarray:
    (markSize, lineWidth) = (tabSizes["markSize"], tabSizes["markLineWidth"])
    (xx, yy) = np.mgrid[1:markSize+1, 1:markSize+1]
    res = np.zeros((markSize, markSize))

    if symbol == 'f':
        r = (markSize+1)/2
        circle = (xx - r) ** 2 + (yy - r) ** 2

        if aa:
            res = np.sqrt(circle)
            res[res > r] = r
            res /= r
            res **= 8
            res = (res * 255).astype(np.uint8)
        else:
            res = (circle >= r ** 2).astype(np.uint8) * 255

        return res

    if symbol == 'o':
        r = (markSize+1)/2
        circle = np.sqrt((xx - r) ** 2 + (yy - r) ** 2)

        if aa:
            # This can't be the easiest/nicest way to do this, but it kind of works
            # Idea: make the center of the circle line the lowest value, then rescale all values in the circle line

            def translate_scale(arr: np.array, mask: np.array, newlo: float, newhi: float, reverse: bool) -> np.array:
                oldlo, oldhi = np.min(arr[mask]), np.max(arr[mask])
                arr[mask] = (arr[mask] - oldlo) / (oldhi - oldlo)
                if reverse:
                    arr[mask] = np.ones(arr[mask].shape) - arr[mask]
                arr[mask] = arr[mask] * (newhi - newlo) + newlo
                return arr

            circle[circle > r] = r
            circle[circle < r - lineWidth] = r
            mask = np.logical_and(circle <= r - lineWidth/2, circle >= r - lineWidth)
            circle = translate_scale(circle, mask, np.max(circle[mask]), np.max(circle[circle < r]), True)
            circle = translate_scale(circle, circle < r, 0, np.max(circle[circle < r]), False)
            circle /= r
            res = circle ** 8
            res = (res * 255).astype(np.uint8)
        else:
            res = np.logical_or(circle < r - lineWidth, circle > r)        
            res = res.astype(np.uint8) * 255

        return res

    if symbol == 'x':
        # using the fact that I only have slopes of 1 and -1 makes this much easier
        down = np.sqrt(2 * (((xx - yy) / 2) ** 2))
        # normalizing by the lowest value outside line width
        down /= np.min(down[down > lineWidth/2])
        down[down >= 1] = 1
        res = np.minimum(down, np.flip(down, axis=0))

        if aa:
            res **= 4
            res = (res * 255).astype(np.uint8)
        else:
            res = (res == 1).astype(np.uint8) * 255

        return res
        
    if verbosity >= 0:
        warn("draw_mark doesn't know what symbol to draw")
    return res


def draw_board() -> np.ndarray:
    (padl, padt, padb, padr) = tabSizes["padding"]
    (nFrets, fretWidth, topWidth, bottomWidth, fretDist) = (
            tabSizes["nFrets"], tabSizes["fretLineWidth"], tabSizes["topLineWidth"], tabSizes["bottomLineWidth"], tabSizes["fretDist"]
            ) 
    (nStrings, stringWidth, stringDist) = (tabSizes["nStrings"], tabSizes["stringLineWidth"], tabSizes["stringDist"]) 
    markSize = tabSizes["markSize"]
    width = nStrings * stringWidth + (nStrings - 1) * stringDist
    height = topWidth + bottomWidth + (nFrets - 2) * fretWidth + (nFrets - 1) * fretDist
    res = np.ones((height, width))

    # Draw frets
    res[:topWidth] = 0
    for i in range(1, nFrets):
        res[topWidth + (i - 1) * fretWidth + i * fretDist: topWidth + i * fretWidth + i * fretDist] = 0
    res[height - bottomWidth: height] = 0

    # Draw strings
    stringStart = stringWidth
    res[:, :stringWidth] = 0
    for i in range(nStrings):
        res[:, i * stringWidth + i * stringDist: (i + 1) * stringWidth + i * stringDist] = 0

    # Embed in whitespace
    larger = np.ones((height + padt + padb + markSize, width + padl + padr + markSize))
    larger[padt + markSize: padt + height + markSize, padl + markSize//2: padl + markSize//2 + width] = res
    
    return larger.astype(np.uint8) * 255


def place_mark(board: np.array, mark: str | np.ndarray, string: int, fret: int, aa: bool = False) -> np.ndarray:
    if type(mark) == str:
        mark = draw_mark(mark, aa)
    (padl, padt, _, _) = tabSizes["padding"]
    (nFrets, fretWidth, topWidth, bottomWidth, fretDist) = (
            tabSizes["nFrets"], tabSizes["fretLineWidth"], tabSizes["topLineWidth"], tabSizes["bottomLineWidth"], tabSizes["fretDist"]
            ) 
    (nStrings, stringWidth, stringDist) = (tabSizes["nStrings"], tabSizes["stringLineWidth"], tabSizes["stringDist"]) 
    markSize = tabSizes["markSize"]

    xPos = padl
    xPos += string * (stringWidth + stringDist)
    if fret <= 0:
        yPos = padt
    else:
        yPos = padt + markSize + topWidth
        yPos += (fret - 1) * (fretDist + fretWidth) + (fretDist - markSize)//2
    part = board[yPos: yPos + markSize, xPos: xPos + markSize]
    part = np.minimum(mark, part)
    board[yPos: yPos + markSize, xPos: xPos + markSize] = part
    return board


def spacer(label: bool = True) -> np.ndarray:
    x, y = get_board_size(label)
    space = np.full((y, x), 255).astype(np.uint8)
    return space

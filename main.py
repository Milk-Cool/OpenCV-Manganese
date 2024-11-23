## SETUP
COLOR_HSV = (307, 255, 60)
MIN_S = 30
BETWEEN = (120, 180)
RANGE = 100
SX_RANGE = (300, 500)
SY_RANGE = (250, 470)
## END SETUP

from os import path
import os
import ffmpeg
import cv2 as cv
import sys

sys.setrecursionlimit(1000000)

def color_value(a):
    if a[1] < MIN_S:
        return 0
    if a[0] < BETWEEN[0] or a[0] > BETWEEN[1]:
        return 0
    return abs(a[0] - COLOR_HSV[0])

FRAMES = "_FRAMES"
FRAME = "fr_"

video_name = input("Enter video name (must be in data/): ")
stream = ffmpeg.input(path.join("data", video_name))

first_frame = int(input("Enter the first frame where the stain can be clearly seen: "))
last_frame = int(input("Enter the last frame where the stain can be clearly seen: "))
stream = stream.trim(start_frame=first_frame, end_frame=last_frame)

print("splitting...")
stream = ffmpeg.filter(stream, "fps", fps=1, round="down")

out = path.join("data", video_name + FRAMES)
if not path.exists(out):
    os.mkdir(out)
stream.output(path.join(out, FRAME + "%04d.jpeg")).run()

outlis = []

def get_n(x):
    return int(x[-9:-5])
print("calculating...")
first = True
coords = (0, 0)
for i in sorted(os.listdir(out), key=get_n):
    abspath = path.join(out, i)
    img = cv.imread(abspath)
    img = cv.cvtColor(img, cv.COLOR_RGB2HSV)

    if first:
        maxv = -1
        for x in range(len(img)):
            for y in range(len(img[x])):
                if (x < SX_RANGE[0] or x > SX_RANGE[1]
                        or y < SY_RANGE[0] or y > SY_RANGE[1]):
                    continue
                #print(img[x][y])
                v = color_value(img[x][y])
                if v > maxv:
                    coords = (x, y)
                    maxv = v
        print(maxv, coords)
        first = False
    
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")
    vis = []
    def recu(x, y, d):
        global min_x, min_y, max_x, max_y, vis, RANGE
        if (x, y) not in vis:
            vis.append((x, y))
        else:
            return
        try:
            if color_value(img[x][y]) == 0 and d > RANGE:
                return
        except:
            return
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
        recu(x + 1, y + 1, d + 1)
        recu(x - 1, y - 1, d + 1)
        recu(x + 1, y - 1, d + 1)
        recu(x - 1, y + 1, d + 1)
    recu(coords[0], coords[1], 0)
    
    size = (max_x - min_x + max_y - min_y) // 2
    outlis.append([str(get_n(i)), str(size)])
    print("frame " + str(get_n(i)), size, min_x, min_y, max_x, max_y)

f = open("res.csv", "w")
f.write("\n".join(list(map(lambda x: ",".join(x), outlis))))
f.close()
print("done!")
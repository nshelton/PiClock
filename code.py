import bitops
import time
import math

from imageData import imageBytes
from font import bitmapFont
from wifi import getNetTime
import secrets

from epdDriver import EPD_7in5
EPD_WIDTH       = 800
EPD_HEIGHT      = 480
TWO_PI          = 6.283185
cx              = EPD_WIDTH/2
cy              = EPD_HEIGHT/2
INVERT          = False

if __name__=='__main__':
    print("start")
    epd = EPD_7in5()

    def drawRect(x,y,w,h):
        for x in range(x,x+w):
            for y in range(y,y+h):
                epd.setPixel(x,y,1)

    def drawGrid():
        skip = 2
        for gx in range(8):
            for y in range(0,EPD_HEIGHT,skip):
                epd.setPixel(gx*100,y,1)
        for gy in range(5):
            for x in range(0,EPD_WIDTH,skip):
                epd.setPixel(x,gy*100 +40,1)

    def drawRings():

        for gx in range(4):
            for y in range(0,360, 4 - gx):
                x = cx + math.sin(y * TWO_PI / 360) * (gx * 100)
                y = cy + math.cos(y * TWO_PI / 360) * (gx * 100)
                x = round(clamp(x,0,EPD_WIDTH-1))
                y = round(clamp(y,0,EPD_HEIGHT-1))
                epd.setPixel(x,y,1)


    def putChar(c, px, py, s):
        charData = bitmapFont[c]
        width = max(charData).bit_length() 

        if c == " " :
            width = 5

        width *= s
        for y in range(16) :
            row = charData[y]
            for x in range(width) :
                if row & 1 << x:
                    for sy in range(1, s+1):
                        for sx in range(1, s+1):
                            epd.setPixel(px + x*s + sx, py + y*s + sy, 1)
        return width

    def writeString(string, text_x, text_y, s=1) :
        xoffs = 0
        for c in string:
            xoffs += putChar(c, text_x + xoffs, text_y, s)

    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    days = "Mon Tue Wed Thu Fri Sat Sun".split()

    def clamp(x, a, b):
        return min(max(a,x), b)
        
    def drawCircle(x,y,r) :
        i_r = round(r)
        for dx in range(-i_r-2, i_r+2) :
            for dy in range(-i_r-2, i_r+2) :
                if dx * dx + dy * dy < r * r:
                    epd.setPixel(clamp(x+dx, 0, EPD_WIDTH-1), clamp(y+dy,0,EPD_HEIGHT-1), 1)

    def drawStars():
        starFile = open("stars.txt", "r")
        for line in starFile:
            line = line.split(",")
            rad = float(line[2])

            ra =  EPD_WIDTH * (1 - (float(line[0]))/24)
            theta =  TWO_PI * float(line[0]) /24
            dec =  EPD_HEIGHT * (1 -(float(line[1]) + 90)/180)
            r =  400 * (1 -(float(line[1]) + 90)/180)

            x = math.cos(theta) * r + cx
            y = math.sin(theta) * r + cy

            drawCircle(round(x), round(y), rad)



###############################################################################################
    def zfill(s):
        s = str(s)
        if (len(s) == 1):
            return "0" + s
        return s

    start = time.time()

    # drawGrid()
    drawRings()

    t = getNetTime()
    timeString = f"{zfill(t.tm_hour)}:{zfill(t.tm_min)}:{zfill(t.tm_sec)}  {days[t.tm_wday]} {months[t.tm_mon -1]} {t.tm_mday}"
    writeString(timeString, 0, 20, 2)
    print("time in" , time.time() - start)


    start = time.time()
    drawStars()
    print("stars in" , time.time() - start)
    # sun = getSun()
    # print(sun)

    lat, lon = secrets['lat'], secrets['lon']

    



    if (INVERT):
        epd.invert()


    start = time.time()
    epd.display(epd.buffer)
    print("display in" , time.time() - start)
  
    start = time.time()
    epd.sleep()
    print("sleep in" , time.time() - start)

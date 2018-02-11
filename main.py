# Crocky
# (Circuit Playground Express)

import array
# import audioio
import board
import digitalio
# import math
# import neopixel
import time
import touchio

from adafruit_circuitplayground.express import cpx

class Crocky:

    def __init__(self):
        # spkrenable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
        # spkrenable.direction = digitalio.Direction.OUTPUT
        # spkrenable.value = True

        cpx.detect_taps = 1

        self.touch1 = touchio.TouchIn(board.A2)

        # self.numPixels = 10
        # self.neopixels = neopixel.NeoPixel(board.NEOPIXEL, self.numPixels,
        #                                    brightness=0.2, auto_write=False)
        self.color_normal = [0x00, 0x44, 0x00]
        self.color_growling = [0x00, 0x88, 0x00]
        self.color_happy = [0x44, 0x00, 0x00]

        self.color_sleep1 = [0x44, 0x44, 0x44]
        self.color_sleep2 = [0x00, 0x00, 0x00]

        self.last_growl = self.now()

        self.a = (0, 0, 0)

    def interp(self, x0, x1, frac):
        return x0 + frac * (x1 - x0)

    def interpVec(self, v0, v1, frac):
      out = []
      for i in range(0, 3):
        out.append(int(self.interp(v0[i], v1[i], frac)))
      return out

    def setRing(self, c):
      cpx.pixels.brightness = 0.3
      for p in range(10):
        cpx.pixels[p] = c

    def fade(self, c0, c1, duration, steps):
      t = 0
      while t < steps:
          t_frac = 1.* t / steps
          t += 1
          c = self.interpVec(c0, c1, t_frac)
          self.setRing(c)
          time.sleep(duration / steps)

    def onTouch(self):
        self.fade(self.color_normal, self.color_happy, duration=0.5, steps=10)
        cpx.play_file("um_i_love_you_mama.wav")
        while self.touch1.value:
            time.sleep(.1)
        self.fade(self.color_happy, self.color_normal, duration=0.5, steps=10)

    def growl(self):
        cpx.play_file("gator.wav")
        for t in range(10):
          self.setRing(self.color_growling)
          time.sleep(.1)
          self.setRing(self.color_normal)
          time.sleep(.1)

    def now(self):
        return time.monotonic()

    def dlog(self, msg):
        print("%12.6f: %s" % (time.monotonic(), msg))

    def update_accel(self):
        self.a = cpx.acceleration
        pass

    def update(self):
        t_now = self.now()
        self.setRing(self.color_normal)
        if cpx.tapped:
            self.dlog("accept petting")
            self.onTouch()

        self.update_accel()

        while self.a[2] < 0:
          self.dlog("upside down! sleeeeepy...")
          self.fade(self.color_sleep1, self.color_sleep2, 1.0, 10)
          self.fade(self.color_sleep2, self.color_sleep1, 1.0, 10)
          self.update_accel()

        # self.dlog("slide: %d" % self.slide.value)

        if t_now - self.last_growl > 10.0:
            self.dlog("time to growl")
            if cpx.switch:
              self.growl()
            self.last_growl = self.now()

def test_neo(c):
    neo = neopixel.NeoPixel(board.NEOPIXEL, 10,
                            brightness=0.2, auto_write=False)
    cl = []
    for p in range(10):
        cl.append(c)
    neo[:] = cl
    neo.show()

def run_test_neo():
    i = 0
    while True:
        test_neo([i,i,i])
        i += 1
        if i==255:
            i = 0
        time.sleep(0.1)

crocky = Crocky()

while True:
    crocky.update()
    time.sleep(.1)

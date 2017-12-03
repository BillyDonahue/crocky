# Crocky
# (Circuit Playground Express)

import array
import audioio
import board
import digitalio
import math
import neopixel
import time
import touchio

class Crocky:

    def __init__(self):
        spkrenable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
        spkrenable.direction = digitalio.Direction.OUTPUT
        spkrenable.value = True

        self.touch1 = touchio.TouchIn(board.A2)

        self.numPixels = 10
        self.neopixels = neopixel.NeoPixel(board.NEOPIXEL, self.numPixels,
                                           brightness=0.2, auto_write=False)
        self.color_normal = [0x00, 0x44, 0x00]
        self.color_growling = [0x00, 0x88, 0x00]
        self.color_happy = [0x44, 0x00, 0x00]
        self.last_growl = self.now()

    def interp(self, x0, x1, frac):
        return x0 + frac * (x1 - x0)

    def interpVec(self, v0, v1, frac):
      out = []
      for i in range(0, 3):
        out.append(int(self.interp(v0[i], v1[i], frac)))
      return out

    def setRing(self, c):
      cl = []
      for p in range(self.numPixels):
          cl.append(c)
      self.neopixels[:] = cl
      self.neopixels.show()

    def fade(self, c0, c1, duration, steps):
      t = 0
      while t < steps:
          t_frac = 1.* t / steps
          t += 1
          c = self.interpVec(c0, c1, t_frac)
          self.setRing(c)
          time.sleep(duration / steps)

    def onTouch(self):
        f = open("um_i_love_you_mama.wav", "rb")
        a = audioio.AudioOut(board.SPEAKER, f)
        a.play()

        self.fade(self.color_normal, self.color_happy, duration=0.5, steps=10)

        while self.touch1.value:
            time.sleep(.1)
        if a.playing:
            a.stop()

        self.fade(self.color_happy, self.color_normal, duration=0.5, steps=10)

    def growl(self):
        f = open("gator.wav", "rb")
        a = audioio.AudioOut(board.SPEAKER, f)
        a.play()
        i = 0
        while a.playing:
            if i == 0:
                self.setRing(self.color_normal)
                i = 1
            else:
                self.setRing(self.color_growling)
                i = 0
            time.sleep(.1)
        self.setRing(self.color_normal)

    def now(self):
        return time.monotonic()

    def dlog(self, msg):
        print("%12.6f: %s" % (time.monotonic(), msg))

    def update(self):
        t_now = self.now()
        self.setRing(self.color_normal)
        if self.touch1.value:
            self.dlog("accept petting")
            self.onTouch()

        if t_now - self.last_growl > 10.0:
            self.dlog("growl")
            self.growl()
            self.last_growl = self.now()

crocky = Crocky()

while True:
    crocky.update()
    time.sleep(.1)

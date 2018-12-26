# Crocky
# (Circuit Playground Express)


import board
import digitalio
import time
import array
import touchio

from adafruit_circuitplayground.express import cpx

class Crocky:

    def __init__(self):
        cpx.detect_taps = 1
        self.touch1 = touchio.TouchIn(board.A2)
        self.color_normal = (0x00, 0x44, 0x00)
        self.color_growling = (0x00, 0x88, 0x00)
        self.color_happy = (0x44, 0x00, 0x00)
        self.color_sleep1 = (0x22, 0x22, 0x22)
        self.color_sleep2 = (0x00, 0x00, 0x00)
        self.last_growl = self.now()
        self.a = (0, 0, 0)

    def interp(self, x0, x1, frac):
        return x0 + frac * (x1 - x0)

    def interpVec(self, v0, v1, frac):
      out = []
      for i in range(0, 3):
        out.append(int(self.interp(v0[i], v1[i], frac)))
      return tuple(out)

    def setRing(self, c):
      cpx.pixels.brightness = 0.2
      for p in range(10):
          cpx.pixels[p] = c
      #cpx.pixels[0] = 0x00ff00

    def fade(self, c0, c1, duration, steps):
      t = 0
      while t < steps:
          t_frac = 1.* t / steps
          t += 1
          c = self.interpVec(c0, c1, t_frac)
          self.setRing(c)
          time.sleep(duration / steps)

    def onTouch(self):
        self.fade(self.color_normal, self.color_happy, duration=0.1, steps=5)
        cpx.play_file("um_i_love_you_mama.wav")
        while self.touch1.value:
            time.sleep(.1)
        self.fade(self.color_happy, self.color_normal, duration=0.1, steps=5)

    def growl(self):
        cpx.play_file("gator.wav")
        for t in range(5):
          self.setRing(self.color_growling)
          time.sleep(.05)
          self.setRing(self.color_normal)
          time.sleep(.05)

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
          self.dlog("upside down! sleepy...")
          self.fade(self.color_sleep1, self.color_sleep2, 0.5, 5)
          self.fade(self.color_sleep2, self.color_sleep1, 0.5, 5)
          cpx.play_file("snore.wav")
          self.update_accel()
        # self.dlog("slide: %d" % self.slide.value)
        if t_now - self.last_growl > 10.0:
            self.dlog("time to growl")
            if cpx.switch:
              self.growl()
            self.last_growl = self.now()

crocky = Crocky()

while True:
    crocky.update()
    time.sleep(.1)

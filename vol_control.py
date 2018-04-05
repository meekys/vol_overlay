import alsaaudio
import keyboard

CARD = 1

VOL_STEP = 5

KEY_VOL_MUTE = 113
KEY_VOL_DOWN = 114
KEY_VOL_UP = 115

class VolControl(object):
    def __init__(self, callback = None):
        self.callback = callback
        self.mixer = alsaaudio.Mixer(alsaaudio.mixers(CARD)[0], cardindex=CARD)

        print "Using %s [%s]" % (self.mixer.cardname(), self.mixer.mixer())

    def run(self):
        print "Listening for input..."

        try:
            self.listen()

            keyboard.wait()

        except KeyboardInterrupt:
            print "Quitting..."

    def listen(self):
        keyboard.on_press_key(KEY_VOL_MUTE, self.toggle_mute)
        keyboard.on_press_key(KEY_VOL_DOWN, self.volume_down)
        keyboard.on_press_key(KEY_VOL_UP, self.volume_up)

    def update_overlay(self):
        mute = self.mixer.getmute()[0]
        volume = self.mixer.getvolume()[0]

        if self.callback != None:
            self.callback(volume, mute)
        #print "mute: " + str(mute)
        #print "volume: " + str(volume)

    def toggle_mute(self, event):
        print "Toggle mute"

        self.mixer.setmute(not self.mixer.getmute()[0])

        self.update_overlay()

    def volume_down(self, event):
        print "Volume down"

        self.volume_adjust(-VOL_STEP)

    def volume_up(self, event):
        print "Volume up"

        self.volume_adjust(VOL_STEP)

    def volume_adjust(self, step):
        if self.mixer.getmute()[0]:
            self.mixer.setmute(0)

            self.update_overlay()
            return

        vol = self.mixer.getvolume()[0]

        vol += step

        if vol < 0: vol = 0
        if vol > 100: vol = 100

        self.mixer.setvolume(vol)
        self.mixer.setmute(0)

        self.update_overlay()

def printState(volume, mute):
    if mute:
        print "Muted"
    else:
        print "Volume: " + str(volume)

if __name__ == "__main__":
    VolControl(printState).run()

import pynput as in

class Keyboard:

    def __init__(self):
        self.keyListener = in.keyboard.Listener(on_press=self.onPress,
         on_release=self.onRelease)

    def onPress(self, key):

    def onRelease(self, key):

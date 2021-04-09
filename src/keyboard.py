import pynput

class Keyboard:

    def __init__(self):
        self.__keyListener = pynput.keyboard.Listener(on_press=self.__onPress,
         on_release=self.__onRelease)
        self.__keysDown = set()

        self.__keyListener.start()

    def __onPress(self, key):
        self.__keysDown.add(key)

    def __onRelease(self, key):
        self.__keysDown.discard(key)

    def isKeyDown(self, key):
        return pynput.keyboard.KeyCode.from_char(key) in self.__keysDown

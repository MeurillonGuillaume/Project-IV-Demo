import time


class Timer:
    def __init__(self):
        self.__starttime = 0

    def start(self):
        """
        Start timer
        """
        self.__starttime = time.time()

    def stop(self):
        """
        Return the total timecount
        """
        return int((time.time() - self.__starttime) * 1000)

from threading import Thread, enumerate


class Threader:
    def launch_threads(self, function, threads, args):
        """
        Launch a thread
        """
        for i in range(threads):
            th = Thread(target=function, args=args)
            th.start()

    def check_threads(self):
        return enumerate()

import time

class Timer():
    def __init__(self) -> None:
        self.tik = 0
        self.tok = 0
        self.name = "Timer"
        self.started = False

    def start(self, name):
        if self.started:
            print("Timer already running, unable to start")
        else:
            self.tik = time.perf_counter()
            self.name = name
            self.started = True

    def end(self):
        if not self.started:
            print("Timer not running, cannot end")
        else:
            self.tok = time.perf_counter()
            self.started = False

            time_taken = self.tok - self.tik
            print(f"{self.name} took {time_taken}")


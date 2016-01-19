import time

initial_millis = int(round(time.time() * 1000))
millis = lambda: int(round(time.time() * 1000)) - initial_millis
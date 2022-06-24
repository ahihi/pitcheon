import contextlib
import os

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as fnull:
        with contextlib.redirect_stdout(fnull) as out:
            yield out

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as fnull:
        with contextlib.redirect_stderr(fnull) as out:
            yield out

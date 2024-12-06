#!/usr/bin/env python3
from contextlib import contextmanager

class MyFile:

    myfile = None
    filepath = None

    def __init__(self, filepath="myfile.txt"):
        self.filepath=filepath

    @contextmanager
    def openf(self):
        with open(self.filepath, "a") as myfile:
            self.myfile = myfile
            yield self

    def mywrite(self, text):
        self.myfile.write(text + "\n")


# with MyFile().openf() as mf:
#     mf.mywrite("first line!!")
#     mf.mywrite("second line!!")

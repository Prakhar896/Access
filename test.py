from models import *

DI.setup()

a = Identity("test", "test", "test", "test", "test", "test", "test", "test")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
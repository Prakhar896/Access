import functools, time
from models import *
from services import *

DI.setup()

identities = Identity.load()
# log1 = AuditLog(john.id, "fileCreate", "hello.txt")
# file1 = File(john.id, "hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
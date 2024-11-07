from models import *

DI.setup()

john = Identity.load(username="john")
AuditLog(john.id, "fileCreate", "hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
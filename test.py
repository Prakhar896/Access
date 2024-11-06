from models import *

DI.setup()

john = Identity.load(username="john")
log1 = AuditLog(john.id, "fileDelete", "Deleted file hello.txt")
log2 = AuditLog("someID", "fileDelete", "Deleted file hello.txt")
log3 = AuditLog(john.id, "fileCreate", "Created file hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
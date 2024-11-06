from models import *

DI.setup()

john = Identity("john", "john@email.com", "1234", "2020-01-01", "1234", {}, "2020-01-01", {})
log = AuditLog(john.id, "fileDelete", "Deleted file hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
from models import *

DI.setup()
# DI.save(None, Ref())

# john = Identity("john", "john@email.com", "123456", "2024", "123456", {}, "2024", {})
# john.save()

john = Identity.load(username="john")
# log1 = AuditLog(john.id, "fileCreate", "hello.txt")
file1 = File(john.id, "hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
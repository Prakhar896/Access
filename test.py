from models import *

DI.setup()

# john = Identity("john", "john@email.com", "123456", "2024", "123456", {}, "2024", {})
john = Identity.load(username="john")
log1 = AuditLog(john.id, "fileCreate", "hello.txt")

while True:
    try:
        exec(input("Code: "))
    except Exception as e:
        print("Error: {}".format(e))
        continue
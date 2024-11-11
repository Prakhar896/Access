import functools, time
from models import *
from services import *

# DI.setup()
# DI.save(None, Ref())

# john = Identity("john", "john@email.com", "123456", "2024", "123456", {}, "2024", {})
# # john = Identity.load(username="john")
# log1 = AuditLog(john.id, "fileCreate", "hello.txt")
# file1 = File(john.id, "hello.txt")

# while True:
#     try:
#         exec(input("Code: "))
#     except Exception as e:
#         print("Error: {}".format(e))
#         continue


def repeat(_func=None, *, num_times=2):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            for _ in range(num_times):
                value = func(*args, **kwargs)
            return value
        return wrapper_repeat

    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)

@repeat()
def hello():
    print("hello")
    
hello()
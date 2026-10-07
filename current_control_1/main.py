import getpass
import socket
import shlex

user = getpass.getuser()
host = socket.gethostname()

while True:
    try:
        line = input(f"{user}@{host}:~$ ")
    except EOFError:
        break

    try:
        args = shlex.split(line)
    except ValueError:
        print("Ошибка: неправильные кавычки")
        continue

    if not args:
        continue

    command = args[0]

    if command == "exit":
        break

    elif command == "ls":
        print("Команда:", command)
        print("Аргументы:", args[1:])

    elif command == "cd":
        print("Команда:", command)
        print("Аргументы:", args[1:])

    else:
        print("Ошибка: неизвестная команда")

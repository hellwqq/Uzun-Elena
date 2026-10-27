
import argparse
import getpass
import socket
import shlex

parser = argparse.ArgumentParser()
parser.add_argument("--vfs", default="vfs.zip")
parser.add_argument("--script", default="")
config = parser.parse_args()

user = getpass.getuser()
host = socket.gethostname()


def run_command(line):
    try:
        args = shlex.split(line)
    except ValueError:
        print("Ошибка: неправильные кавычки")
        return

    if not args:
        return

    command = args[0]

    if command == "exit":
        return "exit"

    elif command == "ls" or command == "cd":
        print("Команда:", command)
        print("Аргументы:", args[1:])

    elif command == "conf-dump":
        print("vfs =", config.vfs)
        print("script =", config.script)

    else:
        print("Ошибка: неизвестная команда")


def prompt():
    return f"{user}@{host}:~$ "


if config.script:
    try:
        with open(config.script, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                print(prompt() + line)
                run_command(line)
    except OSError:
        print("Ошибка: не удалось открыть стартовый скрипт")

while True:
    try:
        line = input(prompt())
    except EOFError:
        break

    if run_command(line) == "exit":
        break

# Практика 1
## Задание 1
```
localhost:~# cd /etc
localhost:/etc# ls

localhost:/etc# cut -d: -f1 passwd | sort
```
## Задание 2
```
localhost:/etc# awk '{print $2, $1}' protocols | sort -nr | head -n 5

localhost:/etc# cd ~
```
## Задание 3
```
localhost:~# nano banner

text="$1"
length=${#text}
line=$(printf '%*s' "$length" ''| tr ' ' '-')
echo "+-${line}-+"
echo "| ${text} |"
echo "+-${line}-+"

localhost:~# chmod +x banner
localhost:~# ./banner "Hello from RTU MIREA!"
```
## Задание 4
```
localhost:~# nano find_ids

filename="$1"
grep -oE '[a-zA-Z_][a-zA-Z0-9_]*' "$filename" | sort -u | xargs

localhost:~# chmod +x find_ids
localhost:~# ./find_ids hello.c
```
## Задание 5
```
localhost:~# nano reg

name="$1"
chmod +x "$name"
cp "$name" /usr/local/bin/

localhost:~# chmod +x reg
localhost:~# ./reg banner
localhost:~# banner "Работает!"
```
## Задание 6
```

```
## Задание 7
```

```
## Задание 8
```

```
## Задание 9
```

```
## Задание 10
```

```

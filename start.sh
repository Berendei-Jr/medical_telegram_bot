#!/bin/bash

# Определить директорию, где находится сам скрипт
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Проверить, существует ли файл process.txt
if [ -f "$SCRIPT_DIR/process.txt" ]; then
  # Прочитать PID из файла
  OLD_PID=$(cat "$SCRIPT_DIR/process.txt")
  
  # Проверить, запущен ли процесс с этим PID, и если да, завершить его
  if ps -p $OLD_PID > /dev/null 2>&1; then
    echo "Останавливаем процесс с PID $OLD_PID"
    kill $OLD_PID
  fi
  
  # Удалить старый файл process.txt
  rm "$SCRIPT_DIR/process.txt"
fi

# Загрузить переменные из .env, используя абсолютный путь
source "$SCRIPT_DIR/.env"

# Запустить bot.py в фоне с помощью nohup, используя абсолютный путь
nohup python3 "$SCRIPT_DIR/bot.py" > "$SCRIPT_DIR/bot.log" 2>&1 &

# Сохранить PID нового процесса в файл process.txt
echo $! > "$SCRIPT_DIR/process.txt"

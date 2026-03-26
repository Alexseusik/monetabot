# Беремо офіційний, легкий образ Python 3.12
FROM python:3.12-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл із залежностями і встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь інший код нашого бота
COPY . .

# Команда, яка запустить бота
CMD ["python", "main.py"]
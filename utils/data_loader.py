import json
import os

# Визначаємо шлях до файлу network.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "network.json")

def load_data():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # Резервні дані на випадок, якщо файл випадково видалять
        return {"currencies": [], "branches": {}}

# Ця змінна зберігатиме всі дані в пам'яті
NETWORK_DATA = load_data()
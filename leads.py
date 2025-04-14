from imporst import *
from creations import *
from keys_and_tokens import *


# Секретный API-ключ для авторизованных серверов (нужно установить в переменной окружения)
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "F8Jb3TMQPrHa4CucMRAvazb_UDNWpcsX9PRWT_k*")

# Определение схемы валидации для входных данных
api_antidubl_blackout_schema = {
    'sub': {'type': 'string', 'required': True},
    'userip': {'type': 'string', 'required': True},  # Проверка IP
    'firstname': {'type': 'string', 'required': True},
    'lastname': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True, 'regex': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'},  # Валидация email
    'phone': {'type': 'string', 'required': True, 'regex': r'^\d{10,15}$'},  # Только цифры, от 10 до 15 символов
    'so': {'type': 'string', 'required': True},
    'ad': {'type': 'string', 'required': True},
    'campaign': {'type': 'string', 'required': True},
    'lg': {'type': 'string', 'required': False},
    'ai': {'type': 'string', 'required': False},
    'ci': {'type': 'string', 'required': False},
    'gi': {'type': 'string', 'required': False},
    'password': {'type': 'string', 'required': False},
    'term': {'type': 'string', 'required': False}
}

log_request_schema = {
    'request_ip': {'type': 'string', 'regex': r'^\d{1,3}(\.\d{1,3}){3}$', 'required': False, 'nullable': True},
    'status_code': {'type': 'integer', 'min': 100, 'max': 599, 'required': False, 'nullable': True},
    'request_time[start]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'request_time[end]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'limit': {'type': 'integer', 'min': 1, 'max': 1000, 'default': 50, 'nullable': True},
    'page': {'type': 'integer', 'min': 1, 'default': 1, 'nullable': True}
}



# ✅ 1️⃣ Валидационная схема Cerberus
leads_get_request_schema = {
    'subid': {'type': 'string', 'required': False, 'nullable': True},
    'userip': {'type': 'string', 'regex': r'^\d{1,3}(\.\d{1,3}){3}$', 'required': False, 'nullable': True},
    'firstname': {'type': 'string', 'required': False, 'nullable': True},
    'lastname': {'type': 'string', 'required': False, 'nullable': True},
    'email': {'type': 'string', 'regex': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', 'required': False, 'nullable': True},
    'phone': {'type': 'string', 'required': False, 'nullable': True},
    'funnel': {'type': 'string', 'required': False, 'nullable': True},
    'bayer': {'type': 'string', 'required': False, 'nullable': True},
    'geo': {'type': 'string', 'required': False, 'maxlength': 3, 'nullable': True},
    'lg': {'type': 'string', 'required': False, 'nullable': True},
    'datatime[start]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'datatime[end]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'limit': {'type': 'integer', 'min': 1, 'max': 1000, 'required': False, 'default': 50, 'nullable': True},
    'page': {'type': 'integer', 'min': 1, 'required': False, 'default': 1, 'nullable': True}
}


# Схема валидации входных данных
blacklist_schema = {
    'userip': {'type': 'string', 'regex': r'^\d{1,3}(\.\d{1,3}){3}$', 'required': False},
    'email': {'type': 'string', 'regex': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', 'required': False},
    'reason': {'type': 'string', 'maxlength': 255, 'required': False, 'default': 'Manual addition'},
    'source': {'type': 'string', 'allowed': ['manual', 'auto'], 'required': False, 'default': 'manual'}
}


blacklist_remove_schema = {
    'id': {'type': 'integer', 'min': 1, 'required': True}
}

# Схема валидации входных данных
blacklist_filter_schema = {
    'userip': {'type': 'string', 'regex': r'^\d{1,3}(\.\d{1,3}){3}$', 'required': False},
    'email': {'type': 'string', 'regex': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', 'required': False},
    'source': {'type': 'string', 'allowed': ['auto', 'manual'], 'required': False},
    'reason': {'type': 'string', 'maxlength': 255, 'required': False},
    'added_at[start]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False},  # YYYY-MM-DD
    'added_at[end]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False},
    'limit': {'type': 'integer', 'min': 1, 'max': 1000, 'required': False, 'default': 50, 'nullable': True},
    'page': {'type': 'integer', 'min': 1, 'required': False, 'default': 1, 'nullable': True}  # ✅ Добавлен page
}



# Функция для асинхронной обработки и записи лида
def api_antidubl_blackout_async(is_blacklisted, is_duplicate, data, request_ip):
    try:
        # Извлекаем данные из JSON
        subid = data["sub"]
        userip = data["userip"]
        firstname = data["firstname"]
        lastname = data["lastname"]
        email = data["email"]
        phone = data["phone"]
        funnel = data["so"]
        bayer = data["ad"]
        geo = data["campaign"]
        lg = data.get("lg")  # Вернёт None, если ключ отсутствует





        conn = get_db_connection()
        cursor = conn.cursor()

        with conn:  # Одна транзакция для всех операций в фоновом потоке

            # Записываем лид в leads_daily (всегда)
            cursor.execute("""
                INSERT INTO leads_daily (subid, userip, firstname, lastname, email, phone, funnel, bayer, geo, lg, kt_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (subid, userip, firstname, lastname, email, phone, funnel, bayer, geo, lg, 'active'))

            lead_id = cursor.lastrowid

            # Если лид в блэклисте, обновляем статус и добавляем в leads_blacklist
            if is_blacklisted:
                cursor.execute("""
                    INSERT OR IGNORE INTO leads_blacklist (userip, email, reason, source)
                    VALUES (?, ?, ?, ?)
                """, (userip, email, "Blacklisted lead", "auto"))

                cursor.execute("""
                    UPDATE leads_daily 
                    SET kt_status = 'blocked'
                    WHERE id = ?
                """, (lead_id,))

            # Если лид дублируется, обновляем статус на 'duplicate' и добавляем в блэклист
            if is_duplicate:
                cursor.execute("""
                    UPDATE leads_daily 
                    SET kt_status = 'duplicate'
                    WHERE id = ?
                """, (lead_id,))

                cursor.execute("""
                    INSERT OR IGNORE INTO leads_blacklist (userip, email, reason, source)
                    VALUES (?, ?, ?, ?)
                """, (userip, email, "Duplicate lead", "auto"))

        # Логируем результат в фоновом потоке
        response_data = {
            "success": True if not is_blacklisted and not is_duplicate else False,
            "data": {
                "message": "Лид успешно записан" if not is_blacklisted and not is_duplicate 
                          else "Лид заблокирован, так как IP или email в блэклисте" if is_blacklisted 
                          else "Лид заблокирован, так как уже был в базе",
                "lead_id": lead_id
            }
        }
        status_code = 201 if not is_blacklisted and not is_duplicate else 403
        leads_api_log_request(request_ip, data, response_data, status_code)

        send_whatsapp_template(bayer, phone, geo, lg)
        send_email(bayer, email, geo, lg)
    except Exception as e:
        print(f"Ошибка в фоновом потоке для лида {data.get('sub', 'unknown')}: {str(e)}")
        # Логируем ошибку в фоновом потоке
        response_data = {"success": False, "data": {"message": "Ошибка при записи лида в фоновом потоке", "error": str(e)}}
        leads_api_log_request(request_ip, data, response_data, 500)


# Ваши глобальные переменные
API_KEY = '34A18A515E0539CEA776CA3FC9A12D3754C98A6C93796EC0E8D0C51D641FE3B8844F6622F7C1530B9CDF74C86D612008'
SENDER_EMAIL = 'support@immediatefastx.org'
API_ENDPOINT = 'https://api.elasticemail.com/v4/emails'

# Функция отправки письма с использованием шаблона
def send_email(bayer, email, country_code, language_code, template_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверка пользователя
    cursor.execute("SELECT id FROM users WHERE login = ?", (bayer,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"error": "Пользователь не найден в системе"}

    user_id = user["id"]

    # Извлечение template_id, если не передан
    if template_id is None:
        cursor.execute('''
            SELECT template_id FROM email_templates 
            WHERE country_code = ? AND language_code = ?
        ''', (country_code.upper(), language_code))
        template = cursor.fetchone()

        if not template:
            cursor.execute('''
                SELECT template_id FROM email_templates 
                WHERE country_code = ? AND (language_code IS NULL OR language_code = '')
            ''', (country_code.upper(),))
            template = cursor.fetchone()

        if template:
            template_id = template["template_id"]
        else:
            conn.close()
            return

    send_status = 'success'
    error_message = None
    transaction_id = None
    message_id = None

    try:
        # Подготовка данных для API-запроса (используем TemplateName)
        payload = {
            "Recipients": [
                {
                    "Email": email,
                    "Fields": {
                        "name": bayer  # Персонализация для шаблона
                    }
                }
            ],
            "Content": {
                "From": SENDER_EMAIL,
                "TemplateName": template_id,  # Используем TemplateName
                "ReplyTo": SENDER_EMAIL,
                "Merge": {},  # Можно добавить персонализированные данные
                "Options": {
                    "TrackOpens": True,
                    "TrackClicks": True
                }
            }
        }

        headers = {
            'X-ElasticEmail-ApiKey': API_KEY,
            'Content-Type': 'application/json'
        }

        # Отправка запроса
        response = requests.post(API_ENDPOINT, json=payload, headers=headers)

        if not response.text:
            raise Exception("Пустой ответ от API Elastic Email")

        try:
            response_data = response.json()
        except json.JSONDecodeError as json_error:
            raise Exception(f"Ошибка декодирования JSON: {json_error} - Текст ответа: {response.text}")

        if response.status_code != 200 or not response_data.get('success', True):
            raise Exception(f"Ошибка API: {response.status_code} - {response.text}")

        # Извлечение TransactionID и MessageID
        transaction_id = response_data.get('TransactionID')
        message_id = response_data.get('MessageID')

    except Exception as e:
        send_status = 'failure'
        error_message = str(e)

    # Логирование в базу данных
    cursor.execute('''
        INSERT INTO email_api_logs (
            user_id, recipient_email, country_code, language_code, template_id, 
            send_status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        email,
        country_code.upper(),
        language_code,
        template_id,
        send_status,
        error_message
    ))

    conn.commit()
    conn.close()

    if send_status == 'failure':
        return {"error": "Ошибка отправки письма: " + error_message}

    return {
        "success": True,
        "user_id": user_id,
        "template_id": template_id,
        "transaction_id": transaction_id,
        "message_id": message_id
    }


@app.route('/api_antidubl_email_set_body', methods=['POST'])
def save_user():
    # Получаем токен авторизации
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Отсутствует токен авторизации"}), 401

    try:
        token = token.split(' ')[-1]  # Извлекаем токен из заголовка
        payload = verify_jwt(token)  # Проверяем токен
        user_id = payload['user_id']  # Получаем user_id из токена
    except Exception:
        return jsonify({"error": "Недействительный или истекший токен"}), 401

    
    data = request.get_json()

    if not data or 'country_code' not in data or 'language_code' not in data or 'template_id' not in data:
        return jsonify({"error": "Отсутствуют необходимые поля (country_code, language_code, template_id)"}), 400

    country_code = data['country_code']
    language_code = data['language_code']
    template_id = data['template_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Вставка или обновление записи
        cursor.execute('''
            INSERT INTO email_templates (country_code, language_code, template_id, subject, body, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(country_code, language_code) 
            DO UPDATE SET template_id = excluded.template_id AND subject = excluded.subject
        ''', (country_code, language_code, template_id, '', '', user_id))

        conn.commit()


        return jsonify({"success": True, "message": "Данные успешно сохранены"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api_antidubl_email_get_body', methods=['GET'])
def get_email_template():
    # send_email('ferz', 'andreroy718@gmail.com', 'JP', '')
    # Получаем параметры запроса
    country_code = request.args.get('country_code')
    if not country_code:
        return jsonify({"error": "Отсутствует необходимый параметр (country_code)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM email_templates 
            WHERE country_code = ?
        ''', (country_code.upper(),))

        templates = cursor.fetchall()

        if not templates:
            return jsonify({"error": "Шаблоны не найдены"}), 404

        # Формируем список записей
        templates_list = []
        for template in templates:
            templates_list.append({
                "id": template["id"],
                "user_id": template["user_id"],
                "country_code": template["country_code"],
                "language_code": template["language_code"],
                "template_id": template["template_id"]
            })

        return jsonify({
            "success": True,
            "templates": templates_list
        }), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api_antidubl_email_delete_body/<int:template_id>', methods=['DELETE'])
def delete_email_template(template_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM email_templates WHERE id = ?', (template_id,))
        template = cursor.fetchone()

        if not template:
            return jsonify({"error": "Шаблон не найден"}), 404

        cursor.execute('DELETE FROM email_templates WHERE id = ?', (template_id,))
        conn.commit()

        return jsonify({"success": True, "message": f"Шаблон с id {template_id} успешно удален"}), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



# Замените на свои данные
WHATSAPP_BUSINESS_PHONE_NUMBER_ID = "565188296686337"  # Ваш ID номера WhatsApp Business
ACCESS_TOKEN = "EAAI2aZAueMfUBOwFOwYbqpqtpciatdotBBuO6ZBIIFhJVvCItQrLe4316o18SWoHmg5W1AfjcaBxZCz836hIERCQ1nbywKZC0GZCMfibYDnFsPlPpDzZCsFCAzpZC0YZAHswV6lApvYDAg0ZB64IgsZCuJHoR1iqwlZB08mQ4xZAXRLwLBgnsGhLvMGLNT8gBKCaot9iEac43SKjZBHfHiDzXp40DFaE6FL5NZC8URMlMIoFUJMgZCcEAAI2aZAueMfUBOwABe3r2BZBRtQnYi9e5CU3XoWeMQZAWXvmyhFDAm4j06FEGkZA0P2j10ZAriziPbNiITewsjcLq2ZCM9wXMbdZBSFrOXyPgEHlHXlBF07ZAgiF6ZBdH5QbMxMUPw02wkokW2jUaSW4ZBFfwCyRkwTNcuh1MSkdgCdIMAiGzhZAAHUMjeTZCQAMk7sJ5F2Bq6laEAAI2aZAueMfUBOwABe3r2BZBRtQnYi9e5CU3XoWeMQZAWXvmyhFDAm4j06FEGkZA0P2j10ZAriziPbNiITewsjcLq2ZCM9wXMbdZBSFrOXyPgEHlHXlBF07ZAgiF6ZBdH5QbMxMUPw02wkokW2jUaSW4ZBFfwCyRkwTNcuh1MSkdgCdIMAiGzhZAAHUMjeTZCQAMk7sJ5F2Bq6la"  # Ваш токен доступа (Bearer Token)




def send_whatsapp_template(bayer: str, to_number: str, country_code: str, preferred_language: str) -> dict:
    """
    Отправляет шаблонное сообщение через WhatsApp Business API, используя данные из базы.

    Args:
        bayer (str): Логин пользователя.
        to_number (str): Номер получателя в формате E.164 (например, "+5514982190556").
        country_code (str): Двухбуквенный код страны (например, "PL").
        preferred_language (str): Предпочитаемый код языка (например, "pl_PL").

    Returns:
        dict: Словарь с результатом (success, data или error).
    """
    try:
        if not to_number.startswith("+"):
            to_number = f"+{to_number}"

        # Получаем данные шаблона из базы
        template_info = get_template_info(bayer, country_code, preferred_language)
        if "error" in template_info:
            return
        
        # Формируем тело запроса
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_info["template_name"],
                "language": {
                    "code": template_info["language_code"]
                }
            }
        }

        if template_info["components"]:
            payload["template"]["components"] = template_info["components"]

        # Заголовки для запроса
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }

        # Отправляем POST-запрос к WhatsApp API
        response = requests.post(
            f'https://graph.facebook.com/v22.0/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages',
            json=payload,
            headers=headers
        )

        # Логируем запрос и ответ
        request_payload_str = str(payload)
        response_payload_str = response.text
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO WhatsAppApiLogs (request_payload, response_payload)
                VALUES (?, ?)
            """, (request_payload_str, response_payload_str))
        conn.close()

        return {"success": True, "data": response.json()}

    except Exception as e:
        request_payload_str = str(payload) if 'payload' in locals() else "Не удалось сформировать payload"
        response_payload_str = str(e)
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO WhatsAppApiLogs (request_payload, response_payload)
                VALUES (?, ?)
            """, (request_payload_str, response_payload_str))
        conn.close()
        return {"success": False, "error": str(e)}

    except Exception as e:
        request_payload_str = str(payload) if 'payload' in locals() else "Не удалось сформировать payload"
        response_payload_str = str(e)
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO WhatsAppApiLogs (request_payload, response_payload)
                VALUES (?, ?)
            """, (request_payload_str, response_payload_str))
        conn.close()
        return {"success": False, "error": str(e)}




# Эндпоинт для получения всех шаблонов пользователя
@app.route('/api_antidubl_wa_get_all_templates', methods=['GET'])
def get_all_templates_endpoint():
    """
    Эндпоинт для получения всех шаблонов WhatsApp для пользователя.
    Параметры запроса:
        - bayer (str): Логин пользователя (обязательный).

    Пример запроса:
        GET /api_antidubl_wa_get_all_templates?bayer=ferz
    """
    try:
        bayer = request.args.get('bayer')

        # Проверяем наличие обязательного параметра
        if not bayer:
            return jsonify({"error": "Обязательный параметр: 'bayer'"}), 400

        # Логика получения всех шаблонов
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE login = ?", (bayer,))
            user = cursor.fetchone()

            if not user:
                return jsonify({"error": "Пользователь не найден в системе"}), 404

            user_id = user["id"]

            # Получаем все шаблоны для пользователя
            templates = conn.execute(
                "SELECT country_code, preferred_language_code, language_code, template_name, components FROM whatsapp_templates WHERE user_id = ?",
                (user_id,)
            ).fetchall()

            # Форматируем результат в список словарей
            result = []
            for template in templates:
                template_dict = {
                    "country_code": template["country_code"],
                    "language_code": template["language_code"],
                    "template_name": template["template_name"],
                    "preferred_language_code": template["preferred_language_code"],
                    "components": json.loads(template["components"]) if template["components"] else None
                }
                result.append(template_dict)

        return jsonify({"templates": result}), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500




# Эндпоинт для настройки шаблона
@app.route('/api_antidubl_wa_set_template', methods=['POST'])
def set_template_endpoint():
    """
    Эндпоинт для настройки шаблона WhatsApp.
    Ожидаемый JSON:
    {
        "bayer": "user_login",
        "country_code": "PL" (опционально),
        "language_code": "pl_PL" (опционально),
        "template_name": "hello_pl",
        "components": [{"type": "body", "parameters": [{"type": "text", "text": "Jan"}]}] (опционально)
    }
    """
    try:
        data = request.get_json()
        if not data or "bayer" not in data or "template_name" not in data:
            return jsonify({"error": "Обязательные поля: 'bayer' и 'template_name'"}), 400

        bayer = data["bayer"]
        country_code = data.get("country_code")
        language_code = data.get("language_code")
        preferred_language_code = data.get("preferred_language_code")
        template_name = data["template_name"]
        components = data.get("components")

        conn = get_db_connection()
        with conn:
            # Проверяем, существует ли пользователь
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE login = ?", (bayer,))
            user = cursor.fetchone()
            if not user:
                # Если пользователя нет, создаем его
                cursor.execute("INSERT INTO users (login) VALUES (?)", (bayer,))
                user_id = cursor.lastrowid
            else:
                user_id = user["id"]

            # Проверяем, существует ли запись для данной комбинации
            existing = conn.execute(
                "SELECT id FROM whatsapp_templates WHERE user_id = ? AND country_code IS ? AND language_code IS ? AND preferred_language_code IS ?",
                (user_id, country_code.upper() if country_code else None, language_code, preferred_language_code)
            ).fetchone()

            components_json = json.dumps(components) if components else None
            if existing:
                # Обновляем существующую запись
                conn.execute(
                    "UPDATE whatsapp_templates SET template_name = ?, components = ? WHERE user_id = ? AND country_code IS ? AND language_code IS ? AND preferred_language_code IS ?",
                    (template_name, components_json, user_id, country_code.upper() if country_code else None, language_code, preferred_language_code)
                )
            else:
                # Добавляем новую запись
                conn.execute(
                    "INSERT INTO whatsapp_templates (user_id, country_code, language_code, preferred_language_code, template_name, components) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, country_code.upper() if country_code else None, language_code, preferred_language_code, template_name, components_json)
                )
        conn.close()
        return jsonify({"status": "success", "message": "Шаблон успешно установлен"}), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500


# Функция получения шаблона из базы данных
def get_template_info(bayer: str, country_code: str, preferred_language: str = None) -> dict:
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = ?", (bayer,))
        user = cursor.fetchone()

        if not user:
            return {"error": "Пользователь не найден в системе"}

        user_id = user["id"]

        # 1. Если preferred_language указан, проверяем комбинацию страна + язык
        if preferred_language:
            template = conn.execute(
                "SELECT template_name, language_code, components FROM whatsapp_templates WHERE country_code = ? AND preferred_language_code = ? AND user_id = ?",
                (country_code.upper(), preferred_language, user_id)
            ).fetchone()
            
            if template:
                return {
                    "template_name": template["template_name"],
                    "language_code": template["language_code"],
                    "components": json.loads(template["components"]) if template["components"] else None
                }
        
        # 2. Если preferred_language None или комбинация не найдена, проверяем только страну
        template = conn.execute(
            "SELECT template_name, language_code, components FROM whatsapp_templates WHERE country_code = ? AND user_id = ?",
            (country_code.upper(), user_id)
        ).fetchone()
        
        if template:
            return {
                "template_name": template["template_name"],
                "language_code": template["language_code"],
                "components": json.loads(template["components"]) if template["components"] else None
            }
        
        # 3. Если ничего не найдено, возвращаем ошибку
        return {"error": "Шаблон не найден"}






# Эндпоинт для вызова get_template_info
@app.route('/api_antidubl_wa_get_template', methods=['GET'])
def get_template_endpoint():
    """
    Эндпоинт для получения информации о шаблоне WhatsApp.
    Параметры запроса:
        - bayer (str): Логин пользователя (обязательный).
        - country_code (str): Двухбуквенный код страны (обязательный).
        - preferred_language (str): Предпочитаемый код языка (обязательный).

    Пример запроса:
        GET /api_antidubl_wa_get_template?bayer=ferz&country_code=PL&preferred_language=pl_PL
    """
    try:
        bayer = request.args.get('bayer')
        country_code = request.args.get('country_code')
        preferred_language = request.args.get('preferred_language')  # Исправлено на 'preferred_language'

        # Проверяем наличие обязательных параметров
        if not bayer or not country_code:
            return jsonify({"error": "Обязательные параметры: 'bayer', 'country_code'"}), 400

        # Вызываем функцию и возвращаем результат
        result = get_template_info(bayer, country_code, preferred_language)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500



# Эндпоинт для удаления шаблона по template_name
@app.route('/api_antidubl_wa_delete_template', methods=['DELETE'])
def delete_template_endpoint():
    """
    Эндпоинт для удаления записей из whatsapp_templates по template_name для конкретного пользователя.
    Параметры запроса:
        - bayer (str): Логин пользователя (обязательный).
        - template_name (str): Название шаблона для удаления (обязательный).

    Пример запроса:
        DELETE /api_antidubl_wa_delete_template?bayer=ferz&template_name=hello_pl
    """
    try:
        bayer = request.args.get('bayer')
        template_name = request.args.get('template_name')

        # Проверяем наличие обязательных параметров
        if not bayer or not template_name:
            return jsonify({"error": "Обязательные параметры: 'bayer', 'template_name'"}), 400

        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            # Проверяем существование пользователя
            cursor.execute("SELECT id FROM users WHERE login = ?", (bayer,))
            user = cursor.fetchone()

            if not user:
                return jsonify({"error": "Пользователь не найден в системе"}), 404

            user_id = user["id"]

            # Удаляем все записи с указанным template_name для данного пользователя
            cursor.execute(
                "DELETE FROM whatsapp_templates WHERE user_id = ? AND template_name = ?",
                (user_id, template_name)
            )
            deleted_rows = cursor.rowcount  # Количество удаленных строк

            if deleted_rows == 0:
                return jsonify({"error": "Шаблон с таким именем не найден для данного пользователя"}), 404

            conn.commit()

        return jsonify({"status": "success", "message": f"Удалено {deleted_rows} записей с template_name='{template_name}'"}), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500






@app.route('/api_antidubl_blackout', methods=['POST'])
def api_antidubl_blackout():
    """
    API для записи лидов. Проверяет лид синхронно, а запись и обработку выполняет асинхронно в отдельном потоке.
    """
    if request.headers.get('X-Forwarded-For'):
        request_ip = request.headers.get('X-Forwarded-For').split(',')[0]  # Берём первый IP из списка
    elif request.headers.get('X-Real-IP'):
        request_ip = request.headers.get('X-Real-IP')
    else:
        request_ip = request.remote_addr  # Стандартный метод, если нет прокси

    # Получение API-ключа из заголовка
    api_key = request.headers.get("X-Api-Key")
    if not api_key or api_key != EXTERNAL_API_KEY:
        response_data = {"success": False, "data": {"message": "Неверный API-ключ"}}
        return jsonify(response_data), 403

    # Получение данных из запроса
    data = request.get_json()

    v = Validator(api_antidubl_blackout_schema)
    if not v.validate(data):
        response_data = {"success": False, "data": {"message": "Ошибка валидации", "details": v.errors}}
        return jsonify(response_data), 400
    
    subid = data["sub"]

    # Синхронная проверка (быстрая операция)
    conn = get_db_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute("""
            SELECT 
                EXISTS(SELECT 1 FROM leads_blacklist WHERE userip = ? OR email = ?) AS is_blacklisted,
                EXISTS(SELECT 1 FROM leads_daily WHERE userip = ? OR email = ?) AS is_duplicate
        """, (data["userip"], data["email"], data["userip"], data["email"]))
        is_blacklisted, is_duplicate = cursor.fetchone()
    conn.close()

    
    # Запускаем запись лида в фоновом потоке
    threading.Thread(target=api_antidubl_blackout_async, args=(is_blacklisted, is_duplicate, data, request_ip), daemon=True).start()


    # Быстрый ответ клиенту на основе проверки
    if is_blacklisted:
        response_data = {"success": False, "data": {"message": "Лид заблокирован, так как IP или email в блэклисте"}}
        leads_api_log_request(request_ip, data, response_data, 403)
        return jsonify(response_data), 403

    if is_duplicate:
        response_data = {"success": False, "data": {"message": "Лид заблокирован, так как уже был в базе"}}
        leads_api_log_request(request_ip, data, response_data, 403)
        return jsonify(response_data), 403



    # Возвращаем быстрый ответ клиенту
    response_data = {"success": True, "data": {"message": "Лид принят для обработки", "lead_id": None}}  # lead_id пока неизвестен
    return jsonify(response_data), 202  # Используем 202 Accepted для асинхронной обработки






def leads_api_log_request(request_ip, request_data, response_data, status_code):
    """
    Функция для записи логов запросов в таблицу api_logs.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leads_api_logs (request_ip, request_data, response_data, status_code)
            VALUES (?, ?, ?, ?)
        """, (
            request_ip,
            json.dumps(request_data, ensure_ascii=False),  # Сохраняем запрос в формате JSON
            json.dumps(response_data, ensure_ascii=False),  # Сохраняем ответ в формате JSON
            status_code
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при логировании запроса: {str(e)}")



@app.route('/api_antidubl_logs', methods=['GET'])
def api_antidubl_logs():
    """
    Ручка для получения логов запросов с возможностью фильтрации и пагинации.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем параметры фильтрации
        request_params = {
            "request_ip": request.args.get("request_ip"),
            "status_code": request.args.get("status_code", type=int),
            "request_time[start]": request.args.get("request_time[start]"),
            "request_time[end]": request.args.get("request_time[end]"),
            "limit": request.args.get("limit", type=int, default=50),
            "page": request.args.get("page", type=int, default=1)  # ✅ Пагинация
        }

        # Валидация параметров через Cerberus
        v = Validator(log_request_schema, purge_unknown=True)
        if not v.validate(request_params):
            return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

        # Используем очищенные данные
        validated_data = v.document
        request_ip = validated_data.get("request_ip")
        status_code = validated_data.get("status_code")
        start_date = validated_data.get("request_time[start]")
        end_date = validated_data.get("request_time[end]")
        limit = validated_data.get("limit") if validated_data.get("limit") else 50  # ✅ Фикс `None`
        page = validated_data.get("page") if validated_data.get("page") else 1  # ✅ Фикс `None`
        offset = (page - 1) * limit  # Смещение записей для пагинации

        # Безопасная обработка дат
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")
        except ValueError:
            return jsonify({"success": False, "data": {"message": "Некорректный формат даты"}}), 400

        # Формируем SQL-запрос с динамическими условиями
        query = "SELECT id, request_ip, request_data, response_data, status_code, request_time FROM leads_api_logs WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM leads_api_logs WHERE 1=1"
        params = []
        count_params = []

        if request_ip:
            query += " AND request_ip = ?"
            count_query += " AND request_ip = ?"
            params.append(request_ip)
            count_params.append(request_ip)
        
        if status_code:
            query += " AND status_code = ?"
            count_query += " AND status_code = ?"
            params.append(status_code)
            count_params.append(status_code)
        
        if start_date:
            query += " AND request_time >= ?"
            count_query += " AND request_time >= ?"
            params.append(start_date)
            count_params.append(start_date)
        
        if end_date:
            query += " AND request_time <= ?"
            count_query += " AND request_time <= ?"
            params.append(end_date)
            count_params.append(end_date)

        query += " ORDER BY request_time DESC LIMIT ? OFFSET ?"
        params.append(limit)
        params.append(offset)

        # Получаем общее количество записей
        cursor.execute(count_query, count_params)
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // limit) + (1 if total_records % limit > 0 else 0)  # Без `ceil()`

        # Выполняем основной запрос с лимитом и смещением
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()

        # Преобразуем результат в JSON-формат
        logs_list = [{
            "id": log[0],
            "request_ip": log[1],
            "request_data": json.dumps(json.loads(log[2])),  # Преобразуем в строку JSON
            "response_data": json.dumps(json.loads(log[3])),  # Преобразуем в строку JSON
            "status_code": log[4],
            "request_time": log[5]
        } for log in logs]

        return jsonify({
            "success": True,
            "data": logs_list,
            "pagination": {
                "total_records": total_records,
                "total_pages": total_pages,
                "current_page": page,
                "limit_per_page": limit
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "data": {"message": "Ошибка при получении логов", "error": str(e)}}), 500




















@app.route('/api_antidubl_get_leads', methods=['GET'])
def api_antidubl_get_leads():
    """
    API для получения лидов с фильтрацией и пагинацией.
    Теперь работает корректная фильтрация по всем параметрам.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ 1️⃣ Получаем токен авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "data": {"message": "Отсутствует токен авторизации"}}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)  # Функция проверки токена
            user_id = int(payload.get('user_id'))
            user_role = payload.get('role')
            username = payload['username']
            
        except (KeyError, ValueError, TypeError):
            return jsonify({"success": False, "data": {"message": "Недействительный или истекший токен"}}), 401

        is_admin = user_role == 'admin'

        # ✅ 2️⃣ Получаем список столбцов таблицы
        cursor.execute("PRAGMA table_info(leads_daily)")
        columns_info = cursor.fetchall()
        all_columns = [row[1] for row in columns_info]  # row[1] - название столбца



        # Определение фильтруемых колонок (включая новые из таблицы leads_daily)
        filterable_columns = [
            "id", "subid", "userip", "firstname", "lastname", "email", "phone",
            "funnel", "bayer", "geo", "lg", "kt_campaign_name", "kt_campaign_group",
            "kt_landing_group", "kt_offer_group", "kt_landing_name", "kt_offer_name",
            "kt_ffiliate_network", "kt_source_pixel", "kt_stream", "kt_global_source",
            "kt_referrer", "kt_keyword", "kt_click_id", "kt_visitor_code", "kt_campaign_id",
            "kt_campaign_group_id", "kt_offer_group_id", "kt_landing_group_id", "kt_landing_id",
            "kt_offer_id", "kt_affiliate_network", "kt_affiliate_network_id", "kt_source_pixel_id",
            "kt_stream_id", "kt_fb_ad_campaign_name", "kt_external_id", "kt_creative_id",
            "kt_connection_type", "kt_operator", "kt_isp", "kt_country", "kt_region",
            "kt_city", "kt_language", "kt_device_type", "kt_user_agent", "kt_os",
            "kt_os_version", "kt_browser", "kt_browser_version", "kt_device_model",
            "kt_ip", "kt_postback_datetime", "kt_click_datetime", "kt_status",
            "kt_previous_status", "kt_original_status",
            "kt_sale_period", "kt_profitability", "kt_revenue", "sale_status", "kt_profit"
        ]

        # Добавляем sub_id_1 ... sub_id_30 в фильтруемые колонки
        for i in range(1, 31):
            filterable_columns.append(f"kt_sub_id_{i}")

        request_params = {col: request.args.get(col) for col in filterable_columns}
        request_params["datatime[start]"] = request.args.get("datatime[start]")
        request_params["datatime[end]"] = request.args.get("datatime[end]")
        request_params["limit"] = request.args.get("limit", type=int, default=50)
        request_params["page"] = request.args.get("page", type=int, default=1)

        v = Validator(leads_get_request_schema, purge_unknown=True)

        if not v.validate(request_params):
            return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

        validated_data = v.document
        
        # ✅ 4️⃣ Обработка дат
        start_date, end_date = validated_data["datatime[start]"], validated_data["datatime[end]"]


        # Выполнение функции для получения данных лога
    

        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")
        except ValueError:
            return jsonify({"success": False, "data": {"message": "Некорректный формат даты"}}), 400
        


        # try:
        #     fetch_conversions_log(start_date, end_date, conn)
        # except requests.exceptions.RequestException as e:
        #     # Обрабатываем ошибки, связанные с запросом
        #     return jsonify({
        #         "success": False,
        #         "data": {
        #             "message": f"Ошибка при выполнении запроса: {str(e)}"
        #         }
        #     }), 500
        # except Exception as e:
        #     # Обрабатываем все другие ошибки
        #     return jsonify({
        #         "success": False,
        #         "data": {
        #             "message": f"Произошла ошибка: {str(e)}"
        #         }
        #     }), 500




        # ✅ 5️⃣ Формируем SQL-запрос
        query = f"SELECT {', '.join(all_columns)} FROM leads_daily"
        params = []
        where_clauses = []

        # Предположим, что у вас есть переменная username, с которой нужно сравнивать
        x_trackbox_username = username  # username — это переменная, с которой нужно сравнивать

        if not is_admin:
            where_clauses.append("bayer = ?")
            params.append(x_trackbox_username)

        # Фильтрация по колонкам
        for column, value in request_params.items():
            if value and column in filterable_columns:
                where_clauses.append(f"{column} = ?")
                params.append(value)

        if start_date:
            where_clauses.append("datatime >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("datatime <= ?")
            params.append(end_date)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY id DESC, datatime DESC LIMIT ? OFFSET ?"
        params.extend([validated_data["limit"], (validated_data["page"] - 1) * validated_data["limit"]])

        cursor.execute(query, params)
        leads = cursor.fetchall()

        # ✅ 6️⃣ Преобразуем результат в JSON
        leads_list = [dict(zip(all_columns, lead)) for lead in leads]

        # ✅ 7️⃣ Подсчет общего количества записей
        count_query = "SELECT COUNT(*) FROM leads_daily"
        count_params = params[:-2]  # Исключаем limit и offset
        if where_clauses:
            count_query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        total_pages = (total_count // validated_data["limit"]) + (1 if total_count % validated_data["limit"] > 0 else 0)

        conn.close()

        return jsonify({
            "success": True,
            "data": leads_list,
            "pagination": {
                "total_records": total_count,
                "total_pages": total_pages,
                "current_page": validated_data["page"],
                "limit": validated_data["limit"]
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "data": {"message": "Ошибка при получении лидов", "error": str(e)}}), 500








@app.route('/api_antidubl_get_general_statistics', methods=['GET'])
def api_antidubl_get_general_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Получаем токен авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "data": {"message": "Отсутствует токен авторизации"}}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)  # Функция проверки токена
            user_id = int(payload.get('user_id'))
            user_role = payload.get('role')
        except (KeyError, ValueError, TypeError):
            return jsonify({"success": False, "data": {"message": "Недействительный или истекший токен"}}), 401

        is_admin = user_role == 'admin'

        # ✅ Получаем настройки API для пользователя
        cursor.execute("SELECT x_trackbox_username FROM user_api_settings WHERE user_id = ?", (user_id,))
        api_settings_row = cursor.fetchone()
        x_trackbox_username = api_settings_row[0] if api_settings_row else None
        if not x_trackbox_username and not is_admin:
            return jsonify({"success": False, "data": {"message": "Настройки API для пользователя не найдены"}}), 404

        # ✅ Функция для выполнения запроса для получения самых популярных значений для указанного поля
        def get_popular_field_value(field_name, bayer=None):
            query = f"""
                SELECT {field_name}, COUNT({field_name}) AS {field_name}_count
                FROM leads_daily
                WHERE {field_name} IS NOT NULL AND {field_name} != '' 
                AND DATE(datatime) = DATE('now')  -- Используем DATE('now') для SQLite
            """
            if bayer:
                query += " AND bayer = ?"
                cursor.execute(query, (bayer,))
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return (result[0], result[1])  # Возвращаем пару значений (ключ, количество)
            return (None, 0)  # Если значения нет, возвращаем None и 0

        # ✅ Получаем статистику по каждому полю
        popular_values = {}
        fields = [
            "kt_country", "funnel", "kt_campaign_name", "kt_landing_name", "kt_offer_name",
            "kt_global_source", "kt_fb_ad_campaign_name", "kt_sub_id_5", "kt_sub_id_7"
        ]

        for field in fields:
            if is_admin:
                # Для администратора статистика по всем пользователям
                popular_values[field] = get_popular_field_value(field)
            else:
                # Для обычного пользователя статистика только для его "bayer" (x_trackbox_username)
                popular_values[field] = get_popular_field_value(field, x_trackbox_username)

        # ✅ Преобразуем результат в нужный формат
        formatted_data = {field: [value[0], value[1]] for field, value in popular_values.items()}

        # ✅ Возвращаем результат
        return jsonify({
            "success": True,
            "data": formatted_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "data": {
                "message": f"Произошла ошибка: {str(e)}"
            }
        }), 500
















@app.route('/api_antidubl_blacklist_add', methods=['POST'])
def api_antidubl_add_to_blacklist():
    """
    Ручка для добавления IP или email в блэклист вручную.
    """
    data = request.get_json()

    # Валидация входных данных
    v = Validator(blacklist_schema, purge_unknown=True)
    if not v.validate(data):
        return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

    validated_data = v.document
    userip = validated_data.get("userip")
    email = validated_data.get("email")
    reason = validated_data.get("reason")
    source = validated_data.get("source")

    # Проверяем, что переданы хотя бы один из параметров (IP или email)
    if not userip and not email:
        return jsonify({"success": False, "data": {"message": "Необходимо указать userip или email"}}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Добавляем запись в блэклист (если еще нет)
        cursor.execute("""
            INSERT OR IGNORE INTO leads_blacklist (userip, email, reason, source)
            VALUES (?, ?, ?, ?)
        """, (userip, email, reason, source))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "data": {"message": "IP или email успешно добавлены в блэклист"}}), 201

    except Exception as e:
        return jsonify({"success": False, "data": {"message": "Ошибка при добавлении в блэклист", "error": str(e)}}), 500


@app.route('/api_antidubl_blacklist_remove', methods=['DELETE'])
def api_antidubl_blacklist_remove():
    """
    Ручка для удаления IP или email из блэклиста по id.
    """
    data = request.get_json()

    # Валидация данных через Cerberus
    v = Validator(blacklist_remove_schema, purge_unknown=True)
    if not v.validate(data):
        return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

    record_id = data["id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли запись и сразу удаляем, если есть
        cursor.execute("""
            DELETE FROM leads_blacklist WHERE id = ? RETURNING id
        """, (record_id,))
        deleted_record = cursor.fetchone()

        conn.commit()
        conn.close()

        if not deleted_record:
            return jsonify({"success": False, "data": {"message": f"Запись с ID {record_id} не найдена в блэклисте"}}), 404

        return jsonify({"success": True, "data": {"message": f"Запись с ID {record_id} успешно удалена из блэклиста"}}), 200

    except Exception as e:
        return jsonify({"success": False, "data": {"message": "Ошибка при удалении из блэклиста", "error": str(e)}}), 500



@app.route('/api_antidubl_get_blacklist', methods=['GET'])
def api_antidubl_get_blacklist():
    """
    Ручка для получения списка заблокированных IP и email с возможностью фильтрации и пагинации.
    """
    try:
        # ✅ 1️⃣ Получаем параметры запроса
        query_params = request.args.to_dict()

        # ✅ 2️⃣ Приводим `page` и `limit` к `int`, если они переданы
        query_params["page"] = int(query_params.get("page", 1)) if query_params.get("page") else 1
        query_params["limit"] = int(query_params.get("limit", 50)) if query_params.get("limit") else 50

        # ✅ 3️⃣ Валидация входных данных
        v = Validator(blacklist_filter_schema, purge_unknown=True)
        if not v.validate(query_params):
            return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

        validated_params = v.document
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ 4️⃣ Получаем `page` и `limit`
        limit = validated_params.get("limit")
        page = validated_params.get("page")
        offset = (page - 1) * limit  # ✅ Вычисляем сдвиг для SQL

        # ✅ 4️⃣ Подсчет общего количества записей
        count_query = "SELECT COUNT(*) FROM leads_blacklist WHERE 1=1"
        count_params = []

        if validated_params.get("userip"):
            count_query += " AND userip = ?"
            count_params.append(validated_params["userip"])

        if validated_params.get("email"):
            count_query += " AND email = ?"
            count_params.append(validated_params["email"])

        if validated_params.get("source"):
            count_query += " AND source = ?"
            count_params.append(validated_params["source"])

        if validated_params.get("reason"):
            count_query += " AND reason LIKE ?"
            count_params.append(f"%{validated_params['reason']}%")

        if validated_params.get("added_at[start]"):
            count_query += " AND added_at >= ?"
            count_params.append(validated_params["added_at[start]"] + " 00:00:00")

        if validated_params.get("added_at[end]"):
            count_query += " AND added_at <= ?"
            count_params.append(validated_params["added_at[end]"] + " 23:59:59")

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        total_pages = (total_count // limit) + (1 if total_count % limit > 0 else 0)  # Рассчитываем страницы

        # ✅ 5️⃣ Формируем SQL-запрос с динамическими условиями
        query = "SELECT id, userip, email, reason, source, added_at FROM leads_blacklist WHERE 1=1"
        params = []  # Используем новый список для запроса

        if validated_params.get("userip"):
            query += " AND userip = ?"
            params.append(validated_params["userip"])

        if validated_params.get("email"):
            query += " AND email = ?"
            params.append(validated_params["email"])

        if validated_params.get("source"):
            query += " AND source = ?"
            params.append(validated_params["source"])

        if validated_params.get("reason"):
            query += " AND reason LIKE ?"
            params.append(f"%{validated_params['reason']}%")

        if validated_params.get("added_at[start]"):
            query += " AND added_at >= ?"
            params.append(validated_params["added_at[start]"] + " 00:00:00")

        if validated_params.get("added_at[end]"):
            query += " AND added_at <= ?"
            params.append(validated_params["added_at[end]"] + " 23:59:59")

        # Добавляем LIMIT и OFFSET
        query += " ORDER BY added_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])  # Добавляем LIMIT и OFFSET

        cursor.execute(query, params)
        blacklist_entries = cursor.fetchall()

        conn.close()

        # ✅ 6️⃣ Преобразуем данные в JSON-формат
        blacklist_list = [{
            "id": entry[0],
            "userip": entry[1],
            "email": entry[2],
            "reason": entry[3],
            "source": entry[4],
            "added_at": entry[5]
        } for entry in blacklist_entries]

        return jsonify({
            "success": True,
            "data": blacklist_list,
            "pagination": {
                "total_records": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "data": {"message": "Ошибка при получении блэклиста", "error": str(e)}}), 500
    



















# Список допустимых столбцов (для безопасности)
VALID_COLUMNS = {
    "funnel", "geo", "lg", "kt_campaign_group", "kt_landing_group", "kt_offer_group", "kt_landing_name",
    "kt_offer_name", "kt_source_pixel", "kt_stream", "kt_global_source", "kt_referrer",
    "kt_campaign_group_id", "kt_offer_group_id", "kt_landing_group_id",
    "kt_landing_id", "kt_offer_id", "kt_fb_ad_campaign_name", "kt_external_id",
    "kt_creative_id", "kt_connection_type", "kt_operator", "kt_isp", "kt_country", "kt_region", "kt_city",
    "kt_language", "kt_device_type", "kt_os", "kt_os_version", "kt_browser",
    "kt_browser_version", "kt_device_model", "kt_status", "kt_previous_status", "kt_original_status",
    "kt_sale_period", "kt_profitability", "kt_revenue", "sale_status",
    "kt_profit", "kt_sub_id_1", "kt_sub_id_5",
    "kt_sub_id_6", "kt_sub_id_7", "kt_sub_id_8", "kt_sub_id_9", "kt_sub_id_11", "kt_sub_id_13",
    "kt_sub_id_14", "kt_sub_id_16", "kt_sub_id_17", "kt_sub_id_18", "kt_sub_id_19", "kt_sub_id_23",
    "kt_sub_id_25", "kt_sub_id_26", "kt_sub_id_27", "kt_sub_id_28", "kt_sub_id_29", "kt_sub_id_30"
}

# Ручка для получения уникальных значений всех столбцов разом
@app.route('/api_antidubl_get_all_unique_values', methods=['GET'])
def get_all_unique_values():
    try:
        # Подключаемся к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Собираем уникальные значения для всех столбцов
        result_data = {}
        for column in VALID_COLUMNS:
            query = f"SELECT DISTINCT {column} FROM leads_daily WHERE {column} IS NOT NULL"
            cursor.execute(query)
            values = [row[column] for row in cursor.fetchall()]
            result_data[column] = values

        # Закрываем соединение
        conn.close()

        # Возвращаем результат
        return jsonify({
            "success": True,
            "data": result_data
        }), 200

    except sqlite3.Error as e:
        return jsonify({"success": False, "data": {"message": f"Ошибка базы данных: {str(e)}"}}), 500










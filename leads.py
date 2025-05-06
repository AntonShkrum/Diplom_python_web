from imporst import *
from creations import *
from keys_and_tokens import *


# Секретный API-ключ для авторизованных серверов (нужно установить в переменной окружения)
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "F8Jb3TMQPrHa4CucMRAvazb_UDNWpcsX9PRWT_k*")

# Полная схема валидации для leads
api_diktum_schema = {
    'user_id': {'type': 'string', 'required': True},
    'sub': {'type': 'string', 'required': True},
    'userip': {'type': 'string', 'required': True},
    'firstname': {'type': 'string', 'required': True},
    'lastname': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True, 'regex': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'},
    'phone': {'type': 'string', 'required': True, 'regex': r'^\d{10,15}$'},

    'funnel': {'type': 'string', 'required': True},          # !!! а не 'so'
    'ad': {'type': 'string', 'required': False},
    'campaign': {'type': 'string', 'required': False},
    'ai': {'type': 'string', 'required': False},
    'ci': {'type': 'string', 'required': False},
    'gi': {'type': 'string', 'required': False},
    'banner_id': {'type': 'string', 'required': False},
    'campaign_name': {'type': 'string', 'required': False},
    'gender': {'type': 'string', 'required': False},
    'age': {'type': 'string', 'required': False},
    'random': {'type': 'string', 'required': False},
    'impression_weekday': {'type': 'string', 'required': False},
    'impression_hour': {'type': 'string', 'required': False},
    'user_timezone': {'type': 'string', 'required': False},
    'term': {'type': 'string', 'required': False},
    'utm_source': {'type': 'string', 'required': False},
    'utm_medium': {'type': 'string', 'required': False},
    'source': {'type': 'string', 'required': False},
    'device_type': {'type': 'string', 'required': False},
    'position': {'type': 'string', 'required': False},
    
    **{f'kt_sub_id_{i}': {'type': 'string', 'required': False} for i in range(1, 11)}
}



log_request_schema = {
    'request_ip': {'type': 'string', 'regex': r'^\d{1,3}(\.\d{1,3}){3}$', 'required': False, 'nullable': True},
    'status_code': {'type': 'integer', 'min': 100, 'max': 599, 'required': False, 'nullable': True},
    'request_time[start]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'request_time[end]': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$', 'required': False, 'nullable': True},
    'limit': {'type': 'integer', 'min': 1, 'max': 1000, 'default': 50, 'nullable': True},
    'page': {'type': 'integer', 'min': 1, 'default': 1, 'nullable': True}
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
def api_diktum_async(is_blacklisted, is_duplicate, data, request_ip):
    try:
        # Извлекаем данные из JSON
        subid = data["sub"]
        userip = data["userip"]
        firstname = data["firstname"]
        lastname = data["lastname"]
        email = data["email"]
        phone = data["phone"]
        funnel = data["funnel"]
        geo = data["campaign"]
        user_id = data["user_id"]

        # Дополнительные поля
        advertiser_id = data.get("ai")
        campaign_id = data.get("ci")
        campaign_name = data.get("campaign_name")
        banner_id = data.get("banner_id")
        geo_region = data.get("gi")
        gender = data.get("gender")
        age = data.get("age")
        random_value = data.get("random")
        impression_weekday = data.get("impression_weekday")
        impression_hour = data.get("impression_hour")
        user_timezone = data.get("user_timezone")
        search_phrase = data.get("term")
        utm_source = data.get("utm_source")
        utm_medium = data.get("utm_medium")
        source = data.get("source")
        device_type = data.get("device_type")
        position = data.get("position")
        
        # kt_sub_id_1 ... kt_sub_id_10
        kt_sub_ids = [data.get(f"kt_sub_id_{i}") for i in range(1, 11)]

        conn = get_db_connection()
        cursor = conn.cursor()

        with conn:  # Одна транзакция для всех операций в фоновом потоке

            # 1. Запись в leads
            cursor.execute("""
                INSERT INTO leads (subid, userip, firstname, lastname, email, phone, funnel, geo, user_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (subid, userip, firstname, lastname, email, phone, funnel, geo, user_id, 'lead'))

            lead_id = cursor.lastrowid

            # 2. Если лид в блэклисте
            if is_blacklisted:
                cursor.execute("""
                    INSERT OR IGNORE INTO leads_blacklist (userip, email, reason, source)
                    VALUES (?, ?, ?, ?)
                """, (userip, email, "Blacklisted lead", "auto"))

                cursor.execute("""
                    UPDATE leads 
                    SET status = 'blocked'
                    WHERE id = ?
                """, (lead_id,))

            # 3. Если лид дублируется
            elif is_duplicate:
                cursor.execute("""
                    UPDATE leads 
                    SET status = 'duplicate'
                    WHERE id = ?
                """, (lead_id,))

                cursor.execute("""
                    INSERT OR IGNORE INTO leads_blacklist (userip, email, reason, source)
                    VALUES (?, ?, ?, ?)
                """, (userip, email, "Duplicate lead", "auto"))

            # 4. ✨ Дополнительно: Запись полного лида в leads
            update_query = """
                UPDATE leads
                SET advertiser_id = ?, campaign_id = ?, campaign_name = ?, banner_id = ?, geo = ?, gender = ?, age = ?, random = ?,
                    impression_weekday = ?, impression_hour = ?, user_timezone = ?, search_phrase = ?, utm_source = ?, utm_medium = ?,
                    source = ?, device_type = ?, position = ?,
                    kt_sub_id_1 = ?, kt_sub_id_2 = ?, kt_sub_id_3 = ?, kt_sub_id_4 = ?, kt_sub_id_5 = ?,
                    kt_sub_id_6 = ?, kt_sub_id_7 = ?, kt_sub_id_8 = ?, kt_sub_id_9 = ?, kt_sub_id_10 = ?
                WHERE subid = ?
            """

            cursor.execute(update_query, (
                advertiser_id, campaign_id, campaign_name, banner_id, geo_region, gender, age, random_value,
                impression_weekday, impression_hour, user_timezone, search_phrase, utm_source, utm_medium,
                source, device_type, position,
                *kt_sub_ids, subid  # В конце подставляем subid для WHERE
            ))

        # Логирование результата
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

        # Отправка уведомлений
        send_whatsapp_template(user_id, phone)
        send_email(user_id, email)

    except Exception as e:
        print(f"Ошибка в фоновом потоке для лида {data.get('sub', 'unknown')}: {str(e)}")
        response_data = {"success": False, "data": {"message": "Ошибка при записи лида в фоновом потоке", "error": str(e)}}
        leads_api_log_request(request_ip, data, response_data, 500)



# Ваши глобальные переменные
API_KEY = 'API_KEY'
SENDER_EMAIL = 'official@diktum.ru'
API_ENDPOINT = 'https://api.elasticemail.com/v4/emails'

def send_email(user_id, email, template_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверка пользователя
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return {"error": "Пользователь не найден в системе"}

        # Извлечение template_name, если не передан
        if template_name is None:
            cursor.execute('''
                SELECT template_name FROM email_templates 
                WHERE user_id = ?
                LIMIT 1
            ''', (user_id,))
            template = cursor.fetchone()

            if template:
                template_name = template["template_name"]
            else:
                conn.close()
                return {"error": "Шаблон для пользователя не найден"}

        send_status = 'success'
        error_message = None
        transaction_id = None
        message_id = None

        try:
            # Подготовка данных для API-запроса
            payload = {
                "Recipients": [
                    {
                        "Email": email,
                        "Fields": {
                            "name": "User"  # Можно персонализировать имя получателя
                        }
                    }
                ],
                "Content": {
                    "From": SENDER_EMAIL,
                    "TemplateName": template_name,
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

        # Логирование в email_api_logs
        cursor.execute('''
            INSERT INTO email_api_logs (
                user_id, recipient_email, template_name, send_status, error_message
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            email,
            template_name,
            send_status,
            error_message
        ))

        conn.commit()

        if send_status == 'failure':
            return {"error": "Ошибка отправки письма: " + error_message}

        return {
            "success": True,
            "user_id": user_id,
            "template_name": template_name,
            "transaction_id": transaction_id,
            "message_id": message_id
        }

    finally:
        conn.close()


@app.route('/api_diktum_email_set_body', methods=['POST'])
def save_email_template():
    # Получаем токен авторизации
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Отсутствует токен авторизации"}), 401

    try:
        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
    except Exception:
        return jsonify({"error": "Недействительный или истекший токен"}), 401

    data = request.get_json()

    if not data or 'template_name' not in data:
        return jsonify({"error": "Отсутствует необходимое поле (template_name)"}), 400

    template_name = data['template_name']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверка: есть ли уже запись для этого user_id
        cursor.execute('''
            SELECT user_id FROM email_templates WHERE user_id = ?
        ''', (user_id,))
        existing = cursor.fetchone()

        if existing:
            # Если запись есть — обновляем template_name
            cursor.execute('''
                UPDATE email_templates
                SET template_name = ?
                WHERE user_id = ?
            ''', (template_name, user_id))
        else:
            # Если записи нет — создаём новую
            cursor.execute('''
                INSERT INTO email_templates (user_id, template_name)
                VALUES (?, ?)
            ''', (user_id, template_name))

        conn.commit()

        return jsonify({"success": True, "message": "Шаблон успешно сохранён"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/api_diktum_email_get_body', methods=['GET'])
def get_email_template():
    # Получаем токен авторизации
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Отсутствует токен авторизации"}), 401

    try:
        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
    except Exception:
        return jsonify({"error": "Недействительный или истекший токен"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM email_templates 
            WHERE user_id = ?
        ''', (user_id,))

        template = cursor.fetchone()

        if not template:
            return jsonify({"error": "Шаблон для пользователя не найден"}), 404

        template_data = {
            "user_id": template["user_id"],
            "template_name": template["template_name"]
        }

        return jsonify({
            "success": True,
            "template": template_data
        }), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



@app.route('/api_diktum_email_delete_body', methods=['DELETE'])
def delete_email_template():
    from flask import request
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"success": False, "message": "Отсутствует токен авторизации"}), 401

    try:
        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
    except Exception:
        return jsonify({"success": False, "message": "Недействительный или истекший токен"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверяем наличие шаблона у пользователя
        cursor.execute('SELECT user_id FROM email_templates WHERE user_id = ?', (user_id,))
        template = cursor.fetchone()

        if not template:
            return jsonify({"success": False, "message": "Шаблон для данного пользователя не найден"}), 404

        # Удаляем шаблон пользователя
        cursor.execute('DELETE FROM email_templates WHERE user_id = ?', (user_id,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Шаблон пользователя user_id={user_id} успешно удалён"
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка базы данных: {str(e)}"
        }), 500

    finally:
        conn.close()





# Замените на свои данные
WHATSAPP_BUSINESS_PHONE_NUMBER_ID = "565188296686337"  # Ваш ID номера WhatsApp Business
ACCESS_TOKEN = "EAAI2aZAueMfUBOwFOwYbqpqtpciatdotBBuO6ZBIIFhJVvCItQrLe4316o18SWoHmg5W1AfjcaBxZCz836hIERCQ1nbywKZC0GZCMfibYDnFsPlPpDzZCsFCAzpZC0YZAHswV6lApvYDAg0ZB64IgsZCuJHoR1iqwlZB08mQ4xZAXRLwLBgnsGhLvMGLNT8gBKCaot9iEac43SKjZBHfHiDzXp40DFaE6FL5NZC8URMlMIoFUJMgZCcEAAI2aZAueMfUBOwABe3r2BZBRtQnYi9e5CU3XoWeMQZAWXvmyhFDAm4j06FEGkZA0P2j10ZAriziPbNiITewsjcLq2ZCM9wXMbdZBSFrOXyPgEHlHXlBF07ZAgiF6ZBdH5QbMxMUPw02wkokW2jUaSW4ZBFfwCyRkwTNcuh1MSkdgCdIMAiGzhZAAHUMjeTZCQAMk7sJ5F2Bq6laEAAI2aZAueMfUBOwABe3r2BZBRtQnYi9e5CU3XoWeMQZAWXvmyhFDAm4j06FEGkZA0P2j10ZAriziPbNiITewsjcLq2ZCM9wXMbdZBSFrOXyPgEHlHXlBF07ZAgiF6ZBdH5QbMxMUPw02wkokW2jUaSW4ZBFfwCyRkwTNcuh1MSkdgCdIMAiGzhZAAHUMjeTZCQAMk7sJ5F2Bq6la"  # Ваш токен доступа (Bearer Token)



def send_whatsapp_template(user_id, phone):
    try:
        # Приведение номера к международному формату
        if not phone.startswith("+"):
            phone = f"+{phone}"

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем шаблон WhatsApp для пользователя
        cursor.execute("""
            SELECT template_name FROM whatsapp_templates
            WHERE user_id = ?
            LIMIT 1
        """, (user_id,))
        template_row = cursor.fetchone()
        conn.close()

        if not template_row:
            return {"success": False, "error": "Шаблон WhatsApp для пользователя не найден"}

        template_name = template_row["template_name"]

        # Формируем payload запроса к API
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "en_US"  # Можно доработать, если нужно динамически
                }
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }

        # Отправляем POST-запрос в WhatsApp API
        response = requests.post(
            f'https://graph.facebook.com/v17.0/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages',
            json=payload,
            headers=headers
        )

        # Логируем отправку
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO wa_api_logs (request_payload, response_payload)
                VALUES (?, ?)
            """, (json.dumps(payload), response.text))
        conn.close()

        if response.status_code != 200:
            return {"success": False, "error": response.text}

        return {"success": True, "data": response.json()}


    except Exception as e:
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO wa_api_logs (request_payload, response_payload)
                VALUES (?, ?)
            """, (str(payload) if 'payload' in locals() else "Ошибка формирования payload", str(e)))
        conn.close()
        return {"success": False, "error": str(e)}




@app.route('/api_diktum_wa_get_templates', methods=['GET'])
def get_all_templates_endpoint():
    """
    Эндпоинт для получения всех шаблонов WhatsApp для пользователя.
    Параметры запроса:
        - user_id (int): ID пользователя (обязательный).
    """
    try:
        # Получаем токен авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Отсутствует токен авторизации"}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = payload['user_id']
        except Exception:
            return jsonify({"error": "Недействительный или истекший токен"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Пользователь с таким user_id не найден"}), 404

        # Получаем все шаблоны WhatsApp для пользователя
        cursor.execute("""
            SELECT id, template_name
            FROM whatsapp_templates
            WHERE user_id = ?
        """, (user_id,))

        templates = cursor.fetchall()

        conn.close()

        # Формируем список результатов
        result = [
            {
                "id": template["id"],
                "template_name": template["template_name"]
            }
            for template in templates
        ]

        return jsonify({
            "success": True,
            "templates": result
        }), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500



@app.route('/api_diktum_wa_set_template', methods=['POST'])
def set_template_endpoint():
    """
    Эндпоинт для создания или обновления шаблона WhatsApp для авторизованного пользователя.
    Ожидаемый JSON:
    {
        "template_name": "welcome_template"
    }
    """
    try:
        # Получаем токен авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Отсутствует токен авторизации"}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = payload['user_id']
        except Exception:
            return jsonify({"error": "Недействительный или истекший токен"}), 401

        # Получаем тело запроса
        data = request.get_json()
        if not data or "template_name" not in data:
            return jsonify({"error": "Обязательное поле: 'template_name'"}), 400

        template_name = data["template_name"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, есть ли уже шаблон для пользователя
        cursor.execute("SELECT id FROM whatsapp_templates WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            # Обновляем существующий шаблон
            cursor.execute(
                "UPDATE whatsapp_templates SET template_name = ? WHERE user_id = ?",
                (template_name, user_id)
            )
        else:
            # Создаём новый шаблон
            cursor.execute(
                "INSERT INTO whatsapp_templates (user_id, template_name) VALUES (?, ?)",
                (user_id, template_name)
            )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Шаблон успешно сохранён"}), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500

@app.route('/api_diktum_wa_delete_template/<int:template_id>', methods=['DELETE'])
def delete_template_endpoint(template_id):
    """
    Эндпоинт для удаления шаблона WhatsApp по его ID для авторизованного пользователя.
    
    Пример запроса:
        DELETE /api_diktum_wa_delete_template/5
    """
    try:
        # Проверка токена авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Отсутствует токен авторизации"}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = payload['user_id']
        except Exception:
            return jsonify({"error": "Недействительный или истекший токен"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаляем запись только если она принадлежит этому пользователю
        cursor.execute(
            "DELETE FROM whatsapp_templates WHERE user_id = ? AND id = ?",
            (user_id, template_id)
        )
        deleted_rows = cursor.rowcount

        conn.commit()
        conn.close()

        if deleted_rows == 0:
            return jsonify({"error": "Шаблон с таким ID не найден для данного пользователя"}), 404

        return jsonify({
            "success": True,
            "message": f"Удалено {deleted_rows} записей с template_id={template_id}"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500







@app.route('/api_diktum', methods=['POST'])
def api_diktum():
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

    v = Validator(api_diktum_schema)
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
                EXISTS(SELECT 1 FROM leads WHERE userip = ? OR email = ?) AS is_duplicate
        """, (data["userip"], data["email"], data["userip"], data["email"]))
        is_blacklisted, is_duplicate = cursor.fetchone()
    conn.close()

    
    # Запускаем запись лида в фоновом потоке
    threading.Thread(target=api_diktum_async, args=(is_blacklisted, is_duplicate, data, request_ip), daemon=True).start()


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



@app.route('/api_diktum_update_lead_status', methods=['PATCH'])
def api_diktum_update_lead_status():
    """
    Эндпоинт для изменения статуса лида на 'sale' и установки distributor_payout.
    Доступ разрешен только администраторам.
    
    Ожидаемый JSON:
    {
        "lead_id": 123,
        "distributor_payout": 50
    }
    """
    try:
        # Проверка токена авторизации
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Отсутствует токен авторизации"}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = payload['user_id']
            role = payload.get('role')
        except Exception:
            return jsonify({"success": False, "message": "Недействительный или истекший токен"}), 401

        # Проверяем роль пользователя
        if role != 'admin':
            return jsonify({"success": False, "message": "Доступ запрещён. Только администраторы могут редактировать лиды."}), 403

        # Получаем тело запроса
        data = request.get_json()
        lead_id = data.get('lead_id')
        distributor_payout = data.get('distributor_payout')

        if not lead_id or distributor_payout is None:
            return jsonify({
                "success": False,
                "message": "Поля 'lead_id' и 'distributor_payout' обязательны"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли лид со статусом "lead"
        cursor.execute(
            "SELECT id, status FROM leads WHERE id = ?",
            (lead_id,)
        )
        lead = cursor.fetchone()

        if not lead:
            conn.close()
            return jsonify({"success": False, "message": "Лид не найден"}), 404

        if lead["status"] != "lead":
            conn.close()
            return jsonify({"success": False, "message": "Статус можно изменить только у лида со статусом 'lead'"}), 400

        # Обновляем статус на "sale" и выставляем distributor_payout
        cursor.execute(
            """
            UPDATE leads
            SET status = 'sale', distributor_payout = ?
            WHERE id = ?
            """,
            (distributor_payout, lead_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Статус лида {lead_id} успешно изменён на 'sale', выплата дистрибьютору установлена."
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при обновлении лида: {str(e)}"
        }), 500


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



@app.route('/api_diktum_logs', methods=['GET'])
def api_diktum_logs():
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




















@app.route('/api_diktum_get_leads', methods=['GET'])
def api_diktum_get_leads():
    """
    API для получения лидов с фильтрацией и пагинацией.
    Работает корректная фильтрация только по актуальным полям таблицы leads.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Проверка токена
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "data": {"message": "Отсутствует токен авторизации"}}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = int(payload.get('user_id'))
            user_role = payload.get('role')
            username = payload.get('username')
        except (KeyError, ValueError, TypeError):
            return jsonify({"success": False, "data": {"message": "Недействительный или истекший токен"}}), 401

        is_admin = user_role == 'admin'

        # 2. Получение всех колонок из таблицы leads
        cursor.execute("PRAGMA table_info(leads)")
        columns_info = cursor.fetchall()
        all_columns = [row[1] for row in columns_info]

        # 3. Фильтрация только по реально существующим полям
        filterable_columns = [
            "id", "subid", "userip", "firstname", "lastname", "email", "phone",
            "funnel", "geo", "advertiser_id", "campaign_id", "campaign_name",
            "banner_id", "gender", "age", "random", "impression_weekday",
            "impression_hour", "user_timezone", "search_phrase", "utm_source",
            "utm_medium", "source", "device_type", "position", "status",
            "distributor_payout"  # <== ДОБАВИЛИ!
        ] + [f"kt_sub_id_{i}" for i in range(1, 11)]


        # 4. Получение параметров запроса
        request_params = {col: request.args.get(col) for col in filterable_columns}
        request_params["datatime[start]"] = request.args.get("datatime[start]")
        request_params["datatime[end]"] = request.args.get("datatime[end]")
        request_params["limit"] = request.args.get("limit", type=int, default=50)
        request_params["page"] = request.args.get("page", type=int, default=1)

        # 5. Валидатор (если хочешь, можно сюда подключить Cerberus-схему)
        validated_data = request_params

        start_date, end_date = validated_data["datatime[start]"], validated_data["datatime[end]"]

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")

        # 6. Формирование SQL-запроса
        query = f"""
            SELECT leads.*, users.login AS username
            FROM leads
            JOIN users ON leads.user_id = users.user_id
        """
        params = []
        where_clauses = []

        if not is_admin:
            where_clauses.append("leads.user_id = ?")
            params.append(user_id)

        for column, value in request_params.items():
            if value and column in filterable_columns:
                where_clauses.append(f"leads.{column} = ?")
                params.append(value)

        if start_date:
            where_clauses.append("leads.datatime >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("leads.datatime <= ?")
            params.append(end_date)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY leads.id DESC LIMIT ? OFFSET ?"
        params.extend([validated_data["limit"], (validated_data["page"] - 1) * validated_data["limit"]])

        cursor.execute(query, params)
        leads = cursor.fetchall()

        # Теперь username есть в каждом результате
        leads_list = [dict(lead) for lead in leads]

        # Подсчёт общего количества (оставляем как есть)
        count_query = "SELECT COUNT(*) FROM leads"
        count_params = params[:-2]
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







@app.route('/api_diktum_get_general_statistics', methods=['GET'])
def api_diktum_get_general_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Авторизация
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "data": {"message": "Отсутствует токен авторизации"}}), 401

        try:
            token = token.split(' ')[-1]
            payload = verify_jwt(token)
            user_id = int(payload.get('user_id'))
            user_role = payload.get('role')
        except (KeyError, ValueError, TypeError):
            return jsonify({"success": False, "data": {"message": "Недействительный или истекший токен"}}), 401

        is_admin = user_role == 'admin'

        # 2. Получаем функцию подсчёта популярных значений
        def get_popular_field_value(field_name, user_id_filter=None):
            query = f"""
                SELECT {field_name}, COUNT(*) AS cnt
                FROM leads
                WHERE {field_name} IS NOT NULL AND {field_name} != ''
                AND DATE(datatime) = DATE('now')
            """
            params = []

            if not is_admin:
                query += " AND user_id = ?"
                params.append(user_id_filter)

            query += f" GROUP BY {field_name} ORDER BY cnt DESC LIMIT 1"

            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                return (result[0], result[1])
            else:
                return (None, 0)

        # 3. Какие поля мы реально можем смотреть
        fields = [
            "geo", "funnel", "campaign_name", "utm_source", "utm_medium", 
            "source", "device_type", "gender", "kt_sub_id_5", "kt_sub_id_7"
        ]

        popular_values = {}
        for field in fields:
            popular_values[field] = get_popular_field_value(field, user_id)

        # 4. Ответ в формате {поле: [значение, количество]}
        formatted_data = {field: [value[0], value[1]] for field, value in popular_values.items()}

        return jsonify({
            "success": True,
            "data": formatted_data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "data": {"message": f"Произошла ошибка: {str(e)}"}
        }), 500













@app.route('/api_diktum_blacklist_add', methods=['POST'])
def api_diktum_add_to_blacklist():
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


@app.route('/api_diktum_blacklist_remove', methods=['DELETE'])
def api_diktum_blacklist_remove():
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



@app.route('/api_diktum_get_blacklist', methods=['GET'])
def api_diktum_get_blacklist():
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
    "funnel", "geo", "status", "gender", "age", "random",
    "impression_weekday", "impression_hour", "user_timezone", "search_phrase",
    "utm_source", "utm_medium", "source", "device_type", "position",
    "advertiser_id", "campaign_id", "campaign_name", "banner_id"
} | {f"kt_sub_id_{i}" for i in range(1, 11)}


@app.route('/api_diktum_get_all_unique_values', methods=['GET'])
def get_all_unique_values():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        result_data = {}
        for column in VALID_COLUMNS:
            try:
                query = f"SELECT DISTINCT {column} FROM leads WHERE {column} IS NOT NULL"
                cursor.execute(query)
                values = [row[0] for row in cursor.fetchall()]
                result_data[column] = values
            except sqlite3.OperationalError:
                # Если вдруг колонка отсутствует, безопасно пропускаем
                continue

        conn.close()

        return jsonify({
            "success": True,
            "data": result_data
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "data": {"message": f"Ошибка базы данных: {str(e)}"}
        }), 500









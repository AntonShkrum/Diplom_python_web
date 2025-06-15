from imporst import *
from creations import *
from keys_and_tokens import *






socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5173'], ping_timeout=60, ping_interval=25)




@app.route('/create_notification', methods=['POST'])
def create_notification_endpoint():
    data = request.get_json()
    text = data.get('text')
    user_ids = data.get('user_ids')
    url = data.get('url')

    if not text or not user_ids:
        return jsonify({
            "success": False,
            "message": "Поля 'text' и 'user_ids' обязательны"
        }), 400

    try:
        create_notification(text, user_ids, url)
        return jsonify({
            "success": True,
            "message": "Уведомление успешно создано"
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при создании уведомления: {str(e)}"
        }), 500


def create_notification(text, user_ids, url=None):
    # Подключаемся к БД
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    date = now.strftime('%d.%m.%Y')  # Дата в формате 'dd.mm.YYYY'
    time = now.strftime('%H:%M')     # Время в формате 'HH:MM'

    # Создаем запись уведомления
    cursor.execute(
        """
        INSERT INTO notifications (text, date, time, url)
        VALUES (?, ?, ?, ?)
        """,
        (text, date, time, url)
    )
    notification_id = cursor.lastrowid

    # Создаем записи для пользователей
    for user_id in user_ids:
        cursor.execute(
            """
            INSERT INTO notification_users (notification_id, user_id, isReaded)
            VALUES (?, ?, ?)
            """,
            (notification_id, user_id, False)
        )

    conn.commit()
    conn.close()

    # Отправляем событие WebSocket после создания уведомления
    socketio.emit('new-notifications', {'message': 'Новое уведомление'}, room=None)











@app.route('/notifications', methods=['GET'])
def get_notifications():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({
            "success": False,
            "message": "Отсутствует токен авторизации"
        }), 401

    try:
        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
    except Exception:
        return jsonify({
            "success": False,
            "message": "Недействительный или истекший токен"
        }), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT notifications.id, notifications.text, notifications.date, notifications.time, notifications.url, 
                   notification_users.isReaded
            FROM notifications
            INNER JOIN notification_users ON notifications.id = notification_users.notification_id
            WHERE notification_users.user_id = ?
            ORDER BY notifications.id DESC
        """
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()

        notifications_list = [
            {
                "id": n['id'],
                "text": n['text'],
                "date": n['date'],
                "time": n['time'],
                "url": n['url'],
                "isReaded": bool(n['isReaded'])
            }
            for n in notifications
        ]

        return jsonify({
            "success": True,
            "message": "Список уведомлений успешно получен",
            "notifications": notifications_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при получении уведомлений: {str(e)}"
        }), 500

    finally:
        conn.close()





@app.route('/read_notifications', methods=['PATCH'])
def read_notifications():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({
            "success": False,
            "message": "Отсутствует токен авторизации"
        }), 401

    try:
        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
    except Exception:
        return jsonify({
            "success": False,
            "message": "Недействительный или истекший токен"
        }), 401

    data = request.get_json()
    ids = data.get('ids')

    if not ids or not isinstance(ids, list):
        return jsonify({
            "success": False,
            "message": "Поле 'ids' обязательно и должно быть списком"
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            UPDATE notification_users
            SET isReaded = 1
            WHERE notification_id IN ({','.join(['?'] * len(ids))}) AND user_id = ?
            """,
            ids + [user_id]
        )

        conn.commit()
        return jsonify({
            "success": True,
            "message": "Уведомления помечены как прочитанные"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при обновлении уведомлений: {str(e)}"
        }), 500

    finally:
        conn.close()



























# Эндпоинт для подключения к WebSocket
@app.route('/socket-events')
def socket_events():
    return "WebSocket server is running"

# Обработчик события WebSocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')







startup_called = False  # Флаг для выполнения логики только один раз

@app.before_request
def startup():
    global startup_called
    if not startup_called:
        startup_called = True
        # Логика старта, например, восстановление задач из базы данных
        # restore_scheduled_tasks()



def restore_scheduled_tasks():
    """
    Логика восстановления задач из базы данных и обновления статуса просроченных задач.
    """
    conn = get_db_connection()  # Подключение к базе данных

    try:
        # Получаем комментарии со статусом 'scheduled'
        cursor = conn.cursor()


    except Exception as e:
        print(f"Ошибка при восстановлении задач: {e}")
    finally:
        conn.close()


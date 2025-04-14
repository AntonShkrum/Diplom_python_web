from imporst import *
from creations import *
from keys_and_tokens import *





set_goal_schema = {
    'username': {'type': 'string', 'required': True, 'empty': False},
    'goal_value': {'type': 'number', 'required': True},
    'goal_month': {'type': 'integer', 'required': True, 'min': 1, 'max': 12}
}

@app.route('/set_goal', methods=['POST'])
def set_goal():

    # 🔐 Проверка JWT и роли
    try:
        token = request.headers.get('Authorization').split(' ')[-1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({"success": False, "message": "Недействительный или истекший токен доступа"}), 401

        role = payload['role']

        if role.lower() != 'admin':
            return jsonify({
                "success": False,
                "message": "Доступ запрещён. Только администратор может устанавливать цели."
            }), 403

    except Exception:
        return jsonify({"success": False, "message": "Ошибка обработки токена"}), 401

    # ✅ Валидация данных
    data = request.get_json()
    v = Validator(set_goal_schema)

    if not v.validate(data):
        response_data = {
            "success": False,
            "data": {
                "message": "Ошибка валидации",
                "details": v.errors
            }
        }
        return jsonify(response_data), 400

    # 💾 Установка цели
    try:
        username = data['username']
        goal_value = data['goal_value']
        goal_month = data['goal_month']

        goal_year = datetime.now().year
        goal_date = f"{goal_month:02d}.{goal_year}"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE goals SET Profit = ? WHERE Data = ? AND Name = ?',
            (goal_value, goal_date, username)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO goals (Data, Name, Profit) VALUES (?, ?, ?)',
                (goal_date, username, goal_value)
            )

        conn.commit()
        return jsonify({
            "success": True,
            "message": f"Цель для пользователя '{username}' на {goal_date} успешно установлена"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при установке цели: {str(e)}"
        }), 500

    finally:
        if 'conn' in locals():
            conn.close()






@app.route('/get_goals', methods=['GET'])
def get_goals_data():
    try:

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM goals ORDER BY Data DESC')
        goals_data = cursor.fetchall()
        conn.close()

        goals_list = [
            {'date': goal['Data'], 'username': goal['Name'], 'goal_value': goal['Profit']}
            for goal in goals_data
        ]

        return jsonify({
            "success": True,
            "message": "Данные по целям успешно получены",
            "goals": goals_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при получении данных: {str(e)}"
        }), 500





def transfer_previous_month_data():
    # Получаем текущую дату и дату предыдущего месяца
    current_date = datetime.now()
    previous_month = current_date - timedelta(days=current_date.day)
    previous_month_str = previous_month.strftime('%m.%Y')  # Формат: MM.YYYY

    # Получаем данные за предыдущий месяц
    conn = get_db_connection()
    cursor = conn.cursor()

    # Выбираем данные за предыдущий месяц
    cursor.execute('SELECT * FROM goals WHERE Data = ?', (previous_month_str,))
    previous_month_data = cursor.fetchall()

    # Вставляем данные за текущий месяц
    current_month_str = current_date.strftime('%m.%Y')  # Формат: MM.YYYY

    # Проверяем, есть ли уже данные за текущий месяц
    cursor.execute('SELECT * FROM goals WHERE Data = ?', (current_month_str,))
    existing_data = cursor.fetchall()

    if not existing_data:  # Если данных за текущий месяц нет, вставляем
        for row in previous_month_data:
            cursor.execute('''
                INSERT INTO goals (Data, Name, Profit)
                VALUES (?, ?, ?)
            ''', (current_month_str, row['Name'], row['Profit']))
        print(f"Данные за {current_month_str} успешно перенесены.")
    else:
        print(f"Данные за {current_month_str} уже существуют. Перенос не требуется.")

    # Сохраняем изменения в базе данных
    conn.commit()
    conn.close()






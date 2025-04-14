from imporst import *
from creations import *
from keys_and_tokens import *






@app.route('/admin/set_goal', methods=['POST'])
def set_goal():
    data = request.get_json()
    username = data['username']
    goal_value = data['goal_value']
    goal_month = int(data['goal_month'])  # Переводим месяц в нужный формат (например, "01" для января)
    goal_year = datetime.now().year
    goal_date = f"{goal_month:02d}.{goal_year}"  # Форматируем месяц с ведущим нулем, если нужно

    conn = get_db_connection()
    cursor = conn.cursor()

    # Пробуем обновить запись, если существует
    cursor.execute('UPDATE requiredProfit SET Profit = ? WHERE Data = ? AND Name = ?', 
                   (goal_value, goal_date, username))
    
    # Если запись не найдена, вставляем новую
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO requiredProfit (Data, Name, Profit) VALUES (?, ?, ?)', 
                       (goal_date, username, goal_value))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Goal set successfully'})





@app.route('/get_goals_data', methods=['GET'])
def get_goals_data():

    transfer_previous_month_data()
    # Получение данных из базы данных с сортировкой по имени, затем по дате
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM requiredProfit ORDER BY Data DESC')
    goals_data = cursor.fetchall()
    conn.close()

    # Форматирование данных для отправки в JSON
    goals_list = [
        {'Data': goal['Data'], 'Name': goal['Name'], 'Profit': goal['Profit']}
        for goal in goals_data
    ]

    return jsonify(goals_list)


def transfer_previous_month_data():
    # Получаем текущую дату и дату предыдущего месяца
    current_date = datetime.now()
    previous_month = current_date - timedelta(days=current_date.day)
    previous_month_str = previous_month.strftime('%m.%Y')  # Формат: MM.YYYY

    # Получаем данные за предыдущий месяц
    conn = get_db_connection()
    cursor = conn.cursor()

    # Выбираем данные за предыдущий месяц
    cursor.execute('SELECT * FROM requiredProfit WHERE Data = ?', (previous_month_str,))
    previous_month_data = cursor.fetchall()

    # Вставляем данные за текущий месяц
    current_month_str = current_date.strftime('%m.%Y')  # Формат: MM.YYYY

    # Проверяем, есть ли уже данные за текущий месяц
    cursor.execute('SELECT * FROM requiredProfit WHERE Data = ?', (current_month_str,))
    existing_data = cursor.fetchall()

    if not existing_data:  # Если данных за текущий месяц нет, вставляем
        for row in previous_month_data:
            cursor.execute('''
                INSERT INTO requiredProfit (Data, Name, Profit)
                VALUES (?, ?, ?)
            ''', (current_month_str, row['Name'], row['Profit']))
        print(f"Данные за {current_month_str} успешно перенесены.")
    else:
        print(f"Данные за {current_month_str} уже существуют. Перенос не требуется.")

    # Сохраняем изменения в базе данных
    conn.commit()
    conn.close()






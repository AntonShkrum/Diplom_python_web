from imporst import *
from creations import *
from keys_and_tokens import *




# def assign_roles_to_users():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Словарь сопоставления пользователей и их ролей
#     user_roles = {
#         'admin': ['antonio', 'floyd', 'mops', 'admin'],
#         'user': ['ferz', 'satoru', 'david', 'nike', 'cart', 'marceline', 'rtx', 'smal', 'sandra']
#     }

#     # Проходим по каждой роли и списку пользователей
#     for role_name, usernames in user_roles.items():
#         # Получаем ID роли
#         cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
#         role_id = cursor.fetchone()
#         if role_id:
#             role_id = role_id['id']
#             for username in usernames:
#                 # Получаем ID пользователя
#                 cursor.execute("SELECT id FROM users WHERE login = ?", (username,))
#                 user = cursor.fetchone()
#                 if user:
#                     user_id = user['id']
#                     # Проверяем, есть ли уже такая запись
#                     cursor.execute("SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
#                     if not cursor.fetchone():
#                         # Добавляем роль пользователю
#                         cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))

#     # Сохраняем изменения
#     conn.commit()
#     conn.close()

# def initialize_page_access():
#     # Подключение к базе данных
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Список страниц для добавления
#     pages = ["/dashboard", "/pixel", "/accounting/baing", "/crm"]

#     # Добавляем страницы в таблицу pages, если они ещё не добавлены
#     for page in pages:
#         cursor.execute("SELECT id FROM pages WHERE url = ?", (page,))
#         page_id = cursor.fetchone()
#         if not page_id:
#             cursor.execute("INSERT INTO pages (url) VALUES (?)", (page,))
#             page_id = cursor.lastrowid
#         else:
#             page_id = page_id['id']

#         # Добавляем доступы к страницам для ролей 'user' и 'teamlead'
#         for role_name in ['user', 'teamlead']:
#             # Получаем ID роли
#             cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
#             role_id = cursor.fetchone()
#             if role_id:
#                 role_id = role_id['id']
#                 # Добавляем доступ, если его еще нет
#                 cursor.execute("SELECT 1 FROM role_pages WHERE role_id = ? AND page_id = ?", (role_id, page_id))
#                 if not cursor.fetchone():
#                     cursor.execute("INSERT INTO role_pages (role_id, page_id) VALUES (?, ?)", (role_id, page_id))

#     # Сохраняем изменения и закрываем соединение
#     conn.commit()
#     conn.close()























































@app.route('/<username>/dashboard', methods=['GET', 'POST'])
def user_profile(username):
    user_role = session.get('role')
    base_template = "admin_base.html" if user_role == 'admin' else "base.html"

    if request.method == 'POST':
        data = request.json  # Получение данных из JSON тела запроса
        conn = get_db_connection()

        for entry in data:
            date_str = entry['date']

            # Преобразование даты из формата DD.MM.YYYY в YYYY-MM-DD
            try:
                date_str = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
            except ValueError:
                return jsonify({'error': f'Invalid date format for {date_str}. Expected DD.MM.YYYY'}), 400

            # Чтение данных из запроса и их обработка
            income_summ = entry.get('Income_Summ')
            expenses_summ = entry.get('Expenses_Summ')
            consumables_summ = entry.get('Consumables_Summ')
            consumables_comm = entry.get('Consumables_Comm')
            garant_summ = entry.get('Garant_Summ')
            garant_comm = entry.get('Garant_Comm')
            returns_summ = entry.get('Returns_Summ')
            returns_comm = entry.get('Returns_Comm')

            # Вставка или обновление данных в базе данных для текущего пользователя
            insert_or_update_data(conn, username, date_str, income_summ, expenses_summ, consumables_summ, consumables_comm, garant_summ, garant_comm, returns_summ, returns_comm)

        conn.close()
        return jsonify({'status': 'success'})
    
    # Рендеринг страницы пользователя
    return render_template('user_profile.html', base_template=base_template, username=username)
    













@app.route('/dashboard', methods=['GET', 'POST'])
def user_profile2():
        # Получаем токен авторизации
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Отсутствует токен авторизации"}), 401

    token = token.split(' ')[-1]
    payload = verify_jwt(token)  # Функция проверки токена (необходимо реализовать)
    username = payload['username']

    user_role = session.get('role')
    base_template = "admin_base.html" if user_role == 'admin' else "base.html"

    if request.method == 'POST':
        data = request.json  # Получение данных из JSON тела запроса
        conn = get_db_connection()

        for entry in data:
            date_str = entry['date']

            # Преобразование даты из формата DD.MM.YYYY в YYYY-MM-DD
            try:
                date_str = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
            except ValueError:
                return jsonify({'error': f'Invalid date format for {date_str}. Expected DD.MM.YYYY'}), 400

            # Чтение данных из запроса и их обработка
            income_summ = entry.get('Income_Summ')
            expenses_summ = entry.get('Expenses_Summ')
            consumables_summ = entry.get('Consumables_Summ')
            consumables_comm = entry.get('Consumables_Comm')
            garant_summ = entry.get('Garant_Summ')
            garant_comm = entry.get('Garant_Comm')
            returns_summ = entry.get('Returns_Summ')
            returns_comm = entry.get('Returns_Comm')

            # Вставка или обновление данных в базе данных для текущего пользователя
            insert_or_update_data(conn, username, date_str, income_summ, expenses_summ, consumables_summ, consumables_comm, garant_summ, garant_comm, returns_summ, returns_comm)

        conn.close()
        return jsonify({'status': 'success'})
    
    # Рендеринг страницы пользователя
    return render_template('user_profile.html', base_template=base_template, username=username)






def insert_or_update_data(conn, table_name, date, income_summ, expenses_summ, consumables_summ, consumables_comm, garant_summ, garant_comm, returns_summ, returns_comm):
    cur = conn.cursor()
    
    # Проверяем текущее значение Expenses_Summ
    cur.execute(f"SELECT Expenses_Summ FROM {table_name} WHERE Data = ?", (date,))
    existing_expenses = cur.fetchone()
    
    if existing_expenses is not None:
        previous_expenses = existing_expenses[0]  # Сохраняем предыдущее значение
        
        cur.execute(f'''
            UPDATE {table_name}
            SET Income_Summ = ?, Expenses_Summ = ?,
                Consumables_Summ = ?, Consumables_Comm = ?,
                Garant_Summ = ?, Garant_Comm = ?,
                Returns_Summ = ?, Returns_Comm = ?
            WHERE Data = ?
        ''', (income_summ, expenses_summ, consumables_summ, consumables_comm, garant_summ, garant_comm, returns_summ, returns_comm, date))
        
        # Проверяем, изменилось ли значение Expenses_Summ
        if previous_expenses != expenses_summ:
            cur.execute(f"UPDATE {table_name} SET manual_input = 'true' WHERE Data = ?", (date,))
    else:
        cur.execute(f'''
            INSERT INTO {table_name} (Data, Income_Summ, Expenses_Summ,
                                    Consumables_Summ, Consumables_Comm,
                                    Garant_Summ, Garant_Comm,
                                    Returns_Summ, Returns_Comm, manual_input)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, income_summ, expenses_summ, consumables_summ, consumables_comm, garant_summ, garant_comm, returns_summ, returns_comm, 'true' if expenses_summ is not None and expenses_summ != "" else None))
    
    conn.commit()
    cur.close()



@app.route('/get_data_from_db', methods=['GET'])
def get_data_from_db():

    
    table_name = request.args.get('table')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Проверяем, что даты переданы и валидны
    if not start_date_str or not end_date_str:
        return jsonify({'error': 'Both start_date and end_date must be provided in DD.MM.YYYY format.'}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
    except ValueError:
        return jsonify({'error': 'Dates must be in DD.MM.YYYY format.'}), 400

    if start_date > end_date:
        return jsonify({'error': 'start_date cannot be later than end_date.'}), 400

    conn = get_db_connection()
    c = conn.cursor()

    # SQL запрос, работающий с датами в формате YYYY-MM-DD
    query = f"""
    SELECT * FROM {table_name}
    WHERE Data BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
    """
    c.execute(query)
    rows = c.fetchall()

    if not rows:
        # Генерируем пустые записи для диапазона дат
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        rows = [
            {"Data": date.strftime("%d.%m.%Y"), "Income_Summ": "", "Expenses_Summ": "", "Consumables_Summ": "", "Consumables_Comm": "", "Garant_Summ": "", "Garant_Comm": "", "Returns_Summ": "", "Returns_Comm": ""}
            for date in date_range
        ]
    else:
        # Преобразуем дату из YYYY-MM-DD в DD.MM.YYYY
        rows = [
            {
                **row,
                "Data": datetime.strptime(row["Data"], "%Y-%m-%d").strftime("%d.%m.%Y")
            }
            for row in rows
        ]

    # Преобразование результатов запроса, замена NULL на пустые строки
    data = [
        {
            "Data": row["Data"],
            "Income_Summ": row.get("Income_Summ", "") or "",
            "Expenses_Summ": row.get("Expenses_Summ", "") or "",
            "Consumables_Summ": row.get("Consumables_Summ", "") or "",
            "Consumables_Comm": row.get("Consumables_Comm", "") or "",
            "Garant_Summ": row.get("Garant_Summ", "") or "",
            "Garant_Comm": row.get("Garant_Comm", "") or "",
            "Returns_Summ": row.get("Returns_Summ", "") or "",
            "Returns_Comm": row.get("Returns_Comm", "") or ""
        }
        for row in rows
    ]

    user_role = session.get('role', 'user')
    return jsonify({'data': data, 'user_role': user_role})



# Валидация входных данных (schema)
autocost_add_campaign_group_schema = {
    'login': {'type': 'string', 'minlength': 1, 'maxlength': 255, 'required': True},
    'kt_campaign_group': {'type': 'string', 'minlength': 1, 'maxlength': 255, 'required': True}
}

@app.route('/autocost_add_campaign_group', methods=['POST'])
def autocost_add_campaign_group():
    """API ручка для добавления данных в таблицу user_campaign_groups"""

    # Получаем данные из запроса
    data = request.get_json()

    # ✅ Валидация входных данных с использованием схемы
    v = Validator(autocost_add_campaign_group_schema, purge_unknown=True)
    if not v.validate(data):
        return jsonify({"success": False, "data": {"message": "Ошибка валидации", "errors": v.errors}}), 400

    # Получаем login и kt_campaign_group из данных запроса
    login = data.get('login')
    kt_campaign_group = data.get('kt_campaign_group')

    try:
        # Подключаемся к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем user_id по login из таблицы users
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        user_id = cursor.fetchone()

        # Если user_id не найден, возвращаем ошибку
        if not user_id:
            conn.close()
            return jsonify({"success": False, "data": {"message": f"Пользователь с login '{login}' не найден"}}), 404

        user_id = user_id[0]  # Извлекаем user_id

        # Вставляем данные в таблицу user_campaign_groups
        query = '''
        INSERT OR IGNORE INTO user_campaign_groups (user_id, kt_campaign_group)
        VALUES (?, ?)
        '''
        cursor.execute(query, (user_id, kt_campaign_group))

        # Подтверждаем изменения и закрываем соединение
        conn.commit()
        conn.close()

        # Возвращаем успешный ответ
        return jsonify({"success": True, "data": {"message": f"Данные успешно добавлены для пользователя '{login}' в кампанию '{kt_campaign_group}'"}}), 201

    except Exception as e:
        # Возвращаем ошибку в случае исключения
        return jsonify({"success": False, "data": {"message": "Ошибка при получении блэклиста", "error": str(e)}}), 500







@app.route('/get_campaign_groups', methods=['GET'])
def get_campaign_groups2():
    for i in range(3):
        date = datetime.now() - timedelta(days=i)
        from_date = date.strftime("%Y-%m-%dT00:00:00")
        to_date = date.strftime("%Y-%m-%dT23:59:59")
        
        auto_input_expenses_kt_api(
            from_date=from_date,
            to_date=to_date
        )

    return jsonify({"success": True, "data": {"message": "Успех"}}), 500



def auto_input_expenses_column():
    for i in range(3):
        date = datetime.now() - timedelta(days=i)
        from_date = date.strftime("%Y-%m-%dT00:00:00")
        to_date = date.strftime("%Y-%m-%dT23:59:59")
        
        auto_input_expenses_kt_api(
            from_date=from_date,
            to_date=to_date
        )



def auto_input_expenses_into_user_table(conn, login, campaign_group, cost, date):
    try:
        # Преобразуем дату в формат YYYY-MM-DD
        formatted_date = date.split("T")[0]

        table_name = login
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        cur = conn.cursor()
        cur.execute(query)

        if cur.fetchone():
            # Проверяем, существует ли запись для указанной даты
            check_query = f"SELECT * FROM {table_name} WHERE Data = ?"
            cur.execute(check_query, (formatted_date,))
            row = cur.fetchone()

            if row:
                # Проверяем значение manual_input (предполагается, что это колонка в таблице)
                # Если manual_input = true, пропускаем обновление
                manual_input_index = cur.description.index([desc for desc in cur.description if desc[0] == 'manual_input'][0])
                manual_input = row[manual_input_index]

                if manual_input == 1 or manual_input == 'true':  # Предполагаем, что manual_input хранится как 1 или 'true'
                    return  # Пропускаем обновление

                # Если manual_input = false, обновляем запись
                update_query = f"""
                UPDATE {table_name}
                SET Expenses_Summ = ?
                WHERE Data = ?
                """
                cur.execute(update_query, (cost, formatted_date))
            else:
                # Если записи нет, вставляем новую (manual_input по умолчанию false)
                insert_query = f"""
                INSERT INTO {table_name} (Data, Expenses_Summ, manual_input)
                VALUES (?, ?, ?)
                """
                cur.execute(insert_query, (formatted_date, cost, 0))  # Устанавливаем manual_input = 0 (false)
            conn.commit()
        else:
            raise Exception(f"Таблица для пользователя {login} не найдена")
    except Exception as e:
        raise  # Пробрасываем ошибку дальше для обработки в основной функции

def auto_input_expenses_kt_api(from_date, to_date):
    url = "https://blackoutorg.com/admin_api/v1/report/build"
    
    headers = {
        "accept": "application/json",
        "Api-Key": "14fb729b1fa737545ae86f9e7fe310d6",
        "Content-Type": "application/json"
    }

    
    payload = {
        "range": {
            "from": from_date,
            "to": to_date,
            "timezone": "UTC"  # Используем UTC как в предыдущем примере
        },
        "dimensions": ["campaign_group"],
        "measures": ["cost"]
    }
    
    conn = get_db_connection()
    errors = []  # Список для хранения ошибок
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            return {
                "success": False,
                "data": {"message": f"Ошибка API: {response.status_code}", "error": response.text}
            }
            
        data = response.json()
        rows = data.get("rows", [])
        
        if not rows:
            return {
                "success": False,
                "data": "Нет данных в ответе API"
            }
            
        user_tables = get_user_tables(conn)
        cur = conn.cursor()
        
        for row in rows:
            campaign_group = row.get("campaign_group")
            cost = row.get("cost")
            
            cur.execute("SELECT user_id FROM user_campaign_groups WHERE kt_campaign_group = ?", (campaign_group,))
            user_id_row = cur.fetchone()
            
            if not user_id_row:
                continue  # Пропускаем запись без user_id без логирования ошибки
            
            user_id = user_id_row[0]
            cur.execute("SELECT login FROM users WHERE id = ?", (user_id,))
            login_row = cur.fetchone()
            
            if not login_row:
                errors.append(f"Не найден login для user_id {user_id}")
                continue
                
            login = login_row[0]
            if login not in user_tables:
                errors.append(f"Таблица для пользователя {login} не существует")
                continue
                
            try:
                auto_input_expenses_into_user_table(conn, login, campaign_group, cost, to_date)
            except Exception as e:
                errors.append(f"Ошибка записи для {login}: {str(e)}")
                continue
        
        if errors:
            return {
                "success": False,
                "data": {"message": "Запись завершена с ошибками", "errors": errors}
            }
        return {
            "success": True,
            "data": {"message": "Все данные успешно записаны"}
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": {"message": "Ошибка запроса к API", "error": str(e)}
        }
    except Exception as e:
        return {
            "success": False,
            "data": {"message": "Ошибка обработки данных", "error": str(e)}
        }
    finally:
        conn.close()



def add_manual_input_column(conn):
    user_tables = get_user_tables(conn)
    cur = conn.cursor()
    
    for table in user_tables:
        # Проверяем, существует ли уже столбец manual_input
        check_query = f"PRAGMA table_info({table})"
        cur.execute(check_query)
        columns = [row[1] for row in cur.fetchall()]
        
        if 'manual_input' not in columns:
            # Добавляем столбец, если его нет
            alter_query = f"ALTER TABLE {table} ADD COLUMN manual_input TEXT DEFAULT NULL"
            cur.execute(alter_query)
        
        # Устанавливаем значение 'true' в manual_input, если Expenses_Summ не NULL
        update_query = f"""
            UPDATE {table} 
            SET manual_input = 'true' 
            WHERE Expenses_Summ IS NOT NULL AND Expenses_Summ != '' 
                  AND (manual_input IS NULL OR manual_input != 'true')
        """
        cur.execute(update_query)
    
    conn.commit()
    cur.close()


















    
from imporst import *
from creations import *
from keys_and_tokens import *




create_user_schema = {
    'username': {'type': 'string', 'required': True, 'empty': False, 'minlength': 2, 'maxlength': 20},
    'password': {'type': 'string', 'required': True, 'empty': False, 'minlength': 8, 'maxlength': 20}
}

@app.route('/create_user', methods=['POST'])
def api_create_user():
    from cerberus import Validator

    data = request.get_json()
    
    v = Validator(create_user_schema)
    if not v.validate(data):
        response_data = {"success": False, "data": {"message": "Ошибка валидации", "details": v.errors}}
        return jsonify(response_data), 400

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login = ?', (username,)).fetchone()
    conn.close()

    if user:
        return jsonify({"success": False, "message": "Пользователь уже существует"}), 400

    create_user(username, password)
    return jsonify({"success": True, "message": "Пользователь успешно создан"}), 201


def create_user(username, password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('INSERT INTO users (login, pass) VALUES (?, ?)', (username, hashed_password))
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()






login = {
    'username': {'type': 'string', 'required': True, 'empty': False, 'minlength': 2, 'maxlength': 20},
    'password': {'type': 'string', 'required': True, 'empty': False, 'minlength': 3, 'maxlength': 20}
}

@app.route('/login', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        
        v = Validator(login)
        if not v.validate(data):
            response_data = {"success": False, "data": {"message": "Ошибка валидации", "details": v.errors}}
            return jsonify(response_data), 400

        username = data['username']
        password = data['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE login = ?', (username,)).fetchone()
        conn.close()

        if user and user['pass'] == hashed_password:
            role = 'admin' if (username == 'admin') else 'user'
            access_token = create_jwt(user['user_id'], username, role)
            refresh_token = create_jwt(user['user_id'], username, role, expires_in=604800, is_refresh=True)  # 7 days expiration for refresh token
            session['username'] = username
            session['user_id'] = user['user_id']
            session['role'] = role

            # Формируем ответ в зависимости от роли
            if role == 'admin':
                response = jsonify({"success": True, "message": "Вход выполнен успешно", "redirect": "/admin", "token": access_token})
            else:
                response = jsonify({"success": True, "message": "Вход выполнен успешно", "redirect": f"/{username}/dashboard", "token": access_token})

            response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='None', secure=True)
            return response, 200  # Добавляем код 200 для успешного входа

        else:
            return jsonify({"success": False, "message": "Неверное имя пользователя или пароль"}), 401








@app.route('/get_users', methods=['GET'])
def get_user():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем всех пользователей
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()

    # Преобразуем данные в список словарей
    users = []
    for row in rows:
        users.append({
            "login": row["login"],
            "user_id": row["user_id"]
        })

    conn.close()
    return jsonify({
        "success": True,
        "message": "Данные пользователей успешно получены",
        "users": users
    }), 200




@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization').split(' ')[-1]
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"success": False, "message": "Недействительный или истекший токен доступа"}), 401

    user_id = payload['user_id']
    role = payload['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем путь к аватару пользователя
    cursor.execute("""
        SELECT avatar_path FROM avatars WHERE user_id = ?
    """, (user_id,))

    avatar = cursor.fetchone()
    conn.close()

    if avatar and avatar['avatar_path']:
        file_path = avatar['avatar_path']
    else:
        file_path = None  # или можно указать строку-заглушку, например "default.png"

    return jsonify({
        "success": True,
        "message": "Информация о пользователе успешно получена",
        "user_id": user_id,
        "role": role,
        "avatar_path": file_path
    }), 200















































upload_avatar_schema = {
    'file': {'type': 'dict', 'required': True}
}

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    from cerberus import Validator

    v = Validator(upload_avatar_schema)
    data = {'file': request.files.get('file')}

    if not v.validate(data):
        response_data = {"success": False, "data": {"message": "Ошибка валидации", "details": v.errors}}
        return jsonify(response_data), 400

    token = request.headers.get('Authorization').split(' ')[-1]
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"success": False, "message": "Недействительный или истекший токен доступа"}), 401

    user_id = payload['user_id']
    file = data['file']

    if file.filename == '':
        return jsonify({"success": False, "message": "Файл не выбран"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_AVATARS_FOLDER'], filename)

        if not os.path.exists(app.config['UPLOAD_AVATARS_FOLDER']):
            os.makedirs(app.config['UPLOAD_AVATARS_FOLDER'])

        conn = get_db_connection()
        try:
            file.save(filepath)
            create_avatars_table_if_not_exists(conn)
            avatar_path = os.path.join('/static/avatars/', filename)

            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO avatars (user_id, avatar_path)
                    VALUES (?, ?)
                """, (user_id, avatar_path))

            return jsonify({
                "success": True,
                "message": "Аватар успешно загружен",
                "avatar_path": avatar_path
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Ошибка сервера: {str(e)}"
            }), 500
        finally:
            conn.close()
    else:
        return jsonify({"success": False, "message": "Недопустимый тип файла"}), 400












change_password_schema = {
    'user_id': {'type': 'integer', 'empty': False, 'required': True},
    'new_password': {'type': 'string', 'required': True, 'empty': False, 'minlength': 8, 'maxlength': 20}
}

@app.route('/change_password', methods=['POST'])
def change_password():
    from cerberus import Validator

    data = request.get_json()
    v = Validator(change_password_schema)

    if not v.validate(data):
        response_data = {"success": False, "data": {"message": "Ошибка валидации", "details": v.errors}}
        return jsonify(response_data), 400

    user_id = data['user_id']
    new_password = data['new_password']

    hashed_new_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            UPDATE users
            SET pass = ?
            WHERE user_id = ?
        """, (hashed_new_password, user_id))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": f"Пользователь с логином '{user_id}' не найден"
            }), 404

        return jsonify({
            "success": True,
            "message": f"Пароль для пользователя '{user_id}' успешно обновлён"
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка базы данных: {str(e)}"
        }), 500

    finally:
        conn.close()




delete_user_schema = {
    'user_id': {'type': 'integer', 'required': True, 'empty': False}
}

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    from cerberus import Validator

    data = request.get_json()
    v = Validator(delete_user_schema)

    if not v.validate(data):
        response_data = {
            "success": False,
            "data": {
                "message": "Ошибка валидации",
                "details": v.errors
            }
        }
        return jsonify(response_data), 400

    user_id = data['user_id']

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            DELETE FROM users
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": f"Пользователь с user_id '{user_id}' не найден"
            }), 404

        return jsonify({
            "success": True,
            "message": f"Пользователь с user_id '{user_id}' успешно удалён"
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка базы данных: {str(e)}"
        }), 500

    finally:
        conn.close()






@app.route('/logout')
def logout():
    session.clear()

    response = jsonify({
        "success": True,
        "message": "Вы успешно вышли из системы"
    })
    response.delete_cookie('refresh_token', httponly=True, samesite='None', secure=True)

    return response, 200













# @app.route('/roles')
# def roles():
#     if session.get('role') != 'admin':
#         return
#     base_template = "admin_base.html"

#     conn = get_db_connection()
#     create_roles_table_if_not_exists(conn)
#     create_user_roles_table_if_not_exists(conn)
#     create_pages_table_if_not_exists(conn)
#     create_role_pages_table_if_not_exists(conn)
#     create_user_pages_table_if_not_exists(conn)
#     conn.close()
    

#     return render_template('roles.html',  base_template=base_template, is_admin=True)



# @app.route('/create_role', methods=['POST'])
# def create_role():
#     # Получаем данные из запроса
#     role_data = request.get_json()
#     role_name = role_data.get('role_name')
    
#     # Проверяем, что имя роли предоставлено
#     if not role_name:
#         return jsonify({'error': 'Название роли пустое.'}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Проверяем, существует ли роль с таким именем
#     cursor.execute('SELECT * FROM roles WHERE name = ?', (role_name,))
#     if cursor.fetchone():
#         conn.close()
#         return jsonify({'error': 'Роль уже существует.'}), 409

#     # Добавляем новую роль в базу данных
#     cursor.execute('INSERT INTO roles (name) VALUES (?)', (role_name,))
#     conn.commit()
#     conn.close()

#     return jsonify({'message': 'Роль успешно создана.'}), 201



# @app.route('/assign_pages_to_role', methods=['POST'])
# def assign_pages_to_role():
#     # Получаем данные из запроса
#     data = request.get_json()
#     role_name = data.get('role_name')
#     pages = data.get('pages')  # Список URL страниц

#     if not role_name:
#         return jsonify({'error': 'Название роли пустое.'}), 400
    
#     if not pages:
#         return jsonify({'error': 'Пустой url страницы.'}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Проверяем существование роли
#     cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
#     role = cursor.fetchone()
#     if not role:
#         conn.close()
#         return jsonify({'error': 'Роль не существует.'}), 404

#     role_id = role['id']

#     # Обработка каждой страницы
#     for page_url in pages:
#         # Проверяем, есть ли страница в базе
#         cursor.execute('SELECT id FROM pages WHERE url = ?', (page_url,))
#         page = cursor.fetchone()
#         if not page:
#             return jsonify({'error': 'Нет такой страницы в базе.'}), 404
#         else:
#             page_id = page['id']

#         # Проверяем, существует ли уже такая связь
#         cursor.execute('SELECT 1 FROM role_pages WHERE role_id = ? AND page_id = ?', (role_id, page_id))
#         if not cursor.fetchone():
#             # Добавляем связь роли с страницей
#             cursor.execute('INSERT INTO role_pages (role_id, page_id) VALUES (?, ?)', (role_id, page_id))

#     conn.commit()
#     conn.close()

#     return jsonify({'message': 'Для роли успешно добавлен доступ к странице(ам)'}), 201




# @app.route('/assign_role_to_user', methods=['POST'])
# def assign_role_to_user():
#     data = request.get_json()
#     username = data.get('username')
#     role_name = data.get('role_name')

#     if not username:
#         return jsonify({'error': 'Требуется ник пользователя'}), 400
    
#     if not role_name:
#         return jsonify({'error': 'Требуется роль пользователя'}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Получаем ID пользователя по его логину
#     cursor.execute('SELECT id FROM users WHERE login = ?', (username,))
#     user = cursor.fetchone()
#     if not user:
#         conn.close()
#         return jsonify({'error': 'Пользователь не найден'}), 404
    
#     user_id = user['user_id']

#     # Получаем ID роли по ее названию
#     cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
#     role = cursor.fetchone()
#     if not role:
#         conn.close()
#         return jsonify({'error': 'Роль не найдена'}), 404
    
#     role_id = role['id']

#     # Проверяем, назначена ли уже такая роль пользователю
#     cursor.execute('SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?', (user_id, role_id))
#     if cursor.fetchone():
#         conn.close()
#         return jsonify({'error': 'Пользователь уже имеет эту роль'}), 409

#     # Назначаем роль пользователю
#     cursor.execute('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)', (user_id, role_id))
#     conn.commit()
#     conn.close()

#     return jsonify({'message': 'Для пользователя успешно добавлена роль'}), 201





# @app.route('/assign_pages_to_user', methods=['POST'])
# def assign_pages_to_user():
#     data = request.get_json()
#     username = data.get('username')
#     pages = data.get('pages')  # Список URL страниц

#     if not username:
#         return jsonify({'error': 'Требуется ник пользователя'}), 400
    

#     if not pages:
#         return jsonify({'error': 'Требуется список страниц'}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Получаем ID пользователя по его логину
#     cursor.execute('SELECT id FROM users WHERE login = ?', (username,))
#     user = cursor.fetchone()
#     if not user:
#         conn.close()
#         return jsonify({'error': 'Пользователь не найден'}), 404
    
#     user_id = user['user_id']

#     # Обработка каждой страницы
#     for page_url in pages:
#         # Проверяем, есть ли страница в базе
#         cursor.execute('SELECT id FROM pages WHERE url = ?', (page_url,))
#         page = cursor.fetchone()
#         if not page:
#             return jsonify({'error': 'Нет такой страницы в базе.'}), 404
#         else:
#             page_id = page['id']

#         # Проверяем, назначена ли уже такая страница пользователю
#         cursor.execute('SELECT 1 FROM user_pages WHERE user_id = ? AND page_id = ?', (user_id, page_id))
#         if not cursor.fetchone():
#             # Добавляем связь пользователя со страницей
#             cursor.execute('INSERT INTO user_pages (user_id, page_id) VALUES (?, ?)', (user_id, page_id))

#     conn.commit()
#     conn.close()

#     return jsonify({'message': 'Для пользователя успешно добавлен доступ к странице(ам)'}), 201





# @app.route('/available_urls', methods=['GET'])
# def available_urls():
#     user_id = session.get('user_id')
#     if not user_id:
#         return jsonify({"error": "User not authenticated"}), 401

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Собираем доступы из таблиц user_pages и role_pages
#     urls = set()

#     # Добавляем страницы, доступные непосредственно пользователю
#     cursor.execute('''
#         SELECT pages.url FROM user_pages
#         JOIN pages ON user_pages.page_id = pages.id
#         WHERE user_pages.user_id = ?
#     ''', (user_id,))
#     urls.update(url['url'] for url in cursor.fetchall())

#     # Добавляем страницы, доступные через роли пользователя
#     cursor.execute('''
#         SELECT pages.url FROM user_roles
#         JOIN role_pages ON user_roles.role_id = role_pages.role_id
#         JOIN pages ON role_pages.page_id = pages.id
#         WHERE user_roles.user_id = ?
#     ''', (user_id,))
#     urls.update(url['url'] for url in cursor.fetchall())

#     conn.close()

#     # Возвращаем список URL в JSON формате
#     return jsonify({"available_urls": list(urls)})
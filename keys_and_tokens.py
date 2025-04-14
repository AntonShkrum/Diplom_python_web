from imporst import *
from creations import *



# JWT ключи
SECRET_KEY = "RKs4m$40ei"
REFRESH_SECRET_KEY = 'Sj5Rss40ku'

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Абсолютный путь к директории проектаfscheduler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папка для сохранения загруженных аватарок
UPLOAD_AVATARS_FOLDER = os.path.join(BASE_DIR, 'static/avatars')
app.config['UPLOAD_AVATARS_FOLDER'] = UPLOAD_AVATARS_FOLDER

# Функция для проверки допустимого расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS










@app.route('/get_scheduled_jobs', methods=['GET'])
def view_scheduled_jobs():

    current_time = datetime.now()
    current_time_formatted = current_time.strftime('%d.%m.%Y %H:%M')

    jobs_info = []

    for job in scheduler.get_jobs():
        if isinstance(job.trigger, DateTrigger):
            run_date = job.trigger.run_date
            run_date_formatted = run_date.strftime('%d.%m.%Y %H:%M')
        else:
            run_date_formatted = 'N/A'

        jobs_info.append({
            "id": job.id,
            "время_запуска": run_date_formatted,
            "функция": job.func.__name__,
            "параметры": job.args
        })

    return jsonify({
        "success": True,
        "message": f"Список задач планировщика успешно получен (текущее время: {current_time_formatted})",
        "jobs": jobs_info
    }), 200







# Проверка JWT
@app.before_request
def verify_token():
    if request.path.startswith('/static/') or request.method == 'OPTIONS':
        return

    if request.endpoint not in ('test', 'index', 'refresh_token', 'api_antidubl_blackout'):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Access token is missing"}), 401

        token = token.split("Bearer ")[-1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({"error": "Invalid or expired access token"}), 401

        request.user = payload


@app.after_request
def after_request(response):

    if response.is_json:
        # Преобразуем response.get_json() обратно в строку с ensure_ascii=False
        data = response.get_json()
        response.set_data(json.dumps(data, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'



    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH,HEAD')
        # Разрешаем запросы с фронта (или с любого сервера)
    if request.path == "/api_antidubl_blackout":
        response.headers.add("Access-Control-Allow-Origin", "*")
    else:
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    return response




def create_jwt(user_id, username, role, expires_in=10800, is_refresh=False):
    payload = {
        "user_id": user_id,
        "role": role,
        "username": username,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    secret = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def verify_jwt(token, is_refresh=False):
    try:
        secret = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None



@app.route('/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 401

    payload = verify_jwt(refresh_token, is_refresh=True)
    if not payload:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    user_id = payload['user_id']
    username = payload['username']
    role = payload['role']
    new_access_token = create_jwt(user_id, username, role)
    new_refresh_token = create_jwt(user_id, username, role, expires_in=604800, is_refresh=True)

    response = jsonify({"token": new_access_token})
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='None', secure=True)

    return response


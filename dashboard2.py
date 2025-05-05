from imporst import *
from creations import *
from keys_and_tokens import *

dashboard_leads_chart_by_days_schema = {
    'startDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'},
    'endDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'},
    'Selected_user': {'type': 'string', 'required': False, 'empty': False}
}

@app.route('/api_dashboard_leads_chart_by_days', methods=['GET'])
def api_dashboard_leads_chart_by_days():
    """
    Эндпоинт для получения расширенной статистики лидов по дням.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({
                "success": False,
                "message": "Отсутствует токен авторизации"
            }), 401

        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload['user_id']
        role = payload['role']
        username = payload['username']

        # Собираем параметры запроса
        query_params = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'Selected_user': request.args.get('Selected_user', 'all')
        }

        # Валидируем параметры
        v = Validator(dashboard_leads_chart_by_days_schema)
        if not v.validate(query_params):
            response_data = {
                "success": False,
                "data": {
                    "message": "Ошибка валидации",
                    "details": v.errors
                }
            }
            return jsonify(response_data), 400

        start_date = query_params['startDate']
        end_date = query_params['endDate']
        selected_user = query_params.get('Selected_user', 'all')

        start_date_sql = datetime.strptime(start_date, "%d.%m.%Y").strftime("%Y-%m-%d 00:00:00")
        end_date_sql = datetime.strptime(end_date, "%d.%m.%Y").strftime("%Y-%m-%d 23:59:59")

        query = """
            SELECT 
                DATE(datatime) as day,
                COUNT(*) as leads_count,
                SUM(CASE WHEN status = 'sale' THEN 1 ELSE 0 END) as sale_count,
                SUM(CASE WHEN status = 'sale' THEN distributor_payout ELSE 0 END) as summary_payout
            FROM leads
            WHERE datatime BETWEEN ? AND ?
        """
        params = [start_date_sql, end_date_sql]

        if role == "admin":
            if selected_user != "all":
                cursor.execute("SELECT user_id FROM users WHERE login = ?", (selected_user,))
                user_row = cursor.fetchone()
                if not user_row:
                    return jsonify({
                        "success": False,
                        "message": f"Пользователь '{selected_user}' не найден"
                    }), 404
                selected_user_id = user_row['user_id']
                query += " AND user_id = ?"
                params.append(selected_user_id)
        else:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " GROUP BY day ORDER BY day ASC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        conn.close()

        data = []
        for row in results:
            leads_count = row["leads_count"]
            sale_count = row["sale_count"]
            summary_payout = float(row["summary_payout"]) if row["summary_payout"] else 0.0

            conversion_rate = (sale_count / leads_count * 100) if leads_count else 0.0
            total_payout_per_sale = (summary_payout / sale_count) if sale_count else 0.0

            data.append({
                "date": datetime.strptime(row["day"], "%Y-%m-%d").strftime("%d.%m.%Y"),
                "leads_count": leads_count,
                "sale_count": sale_count,
                "summary_payout": round(summary_payout, 2),
                "conversion_rate": round(conversion_rate, 2),
                "total_payout_per_sale": round(total_payout_per_sale, 2)
            })

        return jsonify({
            "success": True,
            "message": "Данные для графика успешно получены",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка сервера: {str(e)}",
            "data": []
        }), 500





dashboard_sales_piechart_admin_schema = {
    'startDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'},
    'endDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'},
    'Selected_user': {'type': 'string', 'required': False, 'empty': False}
}

@app.route('/api_dashboard_sales_piechart_admin', methods=['GET'])
def api_dashboard_sales_piechart_admin():
    """
    Эндпоинт для администраторов: статистика по пользователям.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({
                "success": False,
                "message": "Отсутствует токен авторизации"
            }), 401

        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        role = payload.get('role')

        if role != 'admin':
            return jsonify({
                "success": False,
                "message": "Доступ запрещён: только для администраторов"
            }), 403

        query_params = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'Selected_user': request.args.get('Selected_user', 'all')
        }

        v = Validator(dashboard_sales_piechart_admin_schema)
        if not v.validate(query_params):
            response_data = {
                "success": False,
                "data": {
                    "message": "Ошибка валидации",
                    "details": v.errors
                }
            }
            return jsonify(response_data), 400

        start_date = query_params['startDate']
        end_date = query_params['endDate']
        selected_user = query_params.get('Selected_user', 'all')

        start_date_sql = datetime.strptime(start_date, "%d.%m.%Y").strftime("%Y-%m-%d 00:00:00")
        end_date_sql = datetime.strptime(end_date, "%d.%m.%Y").strftime("%Y-%m-%d 23:59:59")

        query = """
            SELECT users.login, 
                   COUNT(leads.id) AS leads_count,
                   SUM(CASE WHEN leads.status = 'sale' THEN 1 ELSE 0 END) AS sale_count,
                   SUM(CASE WHEN leads.status = 'sale' THEN distributor_payout ELSE 0 END) AS total_payout
            FROM leads
            JOIN users ON leads.user_id = users.user_id
            WHERE leads.datatime BETWEEN ? AND ?
        """
        params = [start_date_sql, end_date_sql]

        if selected_user != "all":
            cursor.execute("SELECT user_id FROM users WHERE login = ?", (selected_user,))
            user_row = cursor.fetchone()
            if not user_row:
                return jsonify({
                    "success": False,
                    "message": f"Пользователь '{selected_user}' не найден"
                }), 404
            selected_user_id = user_row['user_id']
            query += " AND leads.user_id = ?"
            params.append(selected_user_id)

        query += " GROUP BY users.login ORDER BY leads_count DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        data = []
        for row in results:
            data.append({
                "username": row["login"],
                "leads_count": row["leads_count"],
                "sale_count": row["sale_count"],
                "total_payout": float(row["total_payout"]) if row["total_payout"] else 0.0
            })

        return jsonify({
            "success": True,
            "message": "Статистика по пользователям успешно получена",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка сервера: {str(e)}",
            "data": []
        }), 500

dashboard_status_piechart_user_schema = {
    'startDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'},
    'endDate': {'type': 'string', 'required': True, 'empty': False, 'regex': r'^\d{2}\.\d{2}\.\d{4}$'}
}

@app.route('/api_dashboard_status_piechart_user', methods=['GET'])
def api_dashboard_status_piechart_user():
    """
    Эндпоинт для пользователей: распределение лидов по статусам.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({
                "success": False,
                "message": "Отсутствует токен авторизации"
            }), 401

        token = token.split(' ')[-1]
        payload = verify_jwt(token)
        user_id = payload.get('user_id')

        query_params = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate')
        }

        v = Validator(dashboard_status_piechart_user_schema)
        if not v.validate(query_params):
            response_data = {
                "success": False,
                "data": {
                    "message": "Ошибка валидации",
                    "details": v.errors
                }
            }
            return jsonify(response_data), 400

        start_date = query_params['startDate']
        end_date = query_params['endDate']

        start_date_sql = datetime.strptime(start_date, "%d.%m.%Y").strftime("%Y-%m-%d 00:00:00")
        end_date_sql = datetime.strptime(end_date, "%d.%m.%Y").strftime("%Y-%m-%d 23:59:59")

        query = """
            SELECT status, COUNT(id) AS status_count
            FROM leads
            WHERE datatime BETWEEN ? AND ?
              AND user_id = ?
            GROUP BY status
        """
        params = [start_date_sql, end_date_sql, user_id]

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        data = []
        for row in results:
            data.append({
                "status": row["status"],
                "count": row["status_count"]
            })

        return jsonify({
            "success": True,
            "message": "Статистика по статусам успешно получена",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка сервера: {str(e)}",
            "data": []
        }), 500

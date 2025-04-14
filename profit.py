from imporst import *
from creations import *
from keys_and_tokens import *


@app.route('/get_requiredProfit', methods=['GET'])
def get_requiredProfit():
    table_name = request.args.get('table', default='default_table_name')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')

    # Преобразуем строки в объекты datetime
    start_date_object = datetime.strptime(startDate, '%d.%m.%Y')
    end_date_object = datetime.strptime(endDate, '%d.%m.%Y')

    start_date = start_date_object.strftime('%m.%Y')
    end_date = end_date_object.strftime('%m.%Y')

    conn = get_db_connection()
    c = conn.cursor()

    # Запрос к базе данных для получения суммарного requiredProfit за период
    c.execute("""
        SELECT SUM(Profit) FROM requiredProfit 
        WHERE Name = ? AND Data BETWEEN ? AND ?
    """, (table_name, start_date, end_date))
    profit = c.fetchone()

    if profit and profit[0]:
        return jsonify({"requiredProfit": profit[0]})
    else:
        return jsonify({"requiredProfit": 0})

@app.route('/get_requiredProfit_all', methods=['GET'])
def get_requiredProfit_all():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')

    # Преобразуем строки в объекты datetime
    start_date_object = datetime.strptime(startDate, '%d.%m.%Y')
    end_date_object = datetime.strptime(endDate, '%d.%m.%Y')

    start_date = start_date_object.strftime('%m.%Y')
    end_date = end_date_object.strftime('%m.%Y')

    conn = get_db_connection()
    c = conn.cursor()

    # Запрос на получение суммарного дохода для всех пользователей за период
    c.execute("""
        SELECT Name, SUM(Profit) FROM requiredProfit 
        WHERE Data BETWEEN ? AND ?
        GROUP BY Name
    """, (start_date, end_date))
    profits = c.fetchall()

    # Проверяем, что результат не пустой
    if profits:
        return jsonify([{"name": profit["Name"], "total_profit": profit["SUM(Profit)"]} for profit in profits])
    else:
        return jsonify({"message": "No data found"})



def get_total_profit(conn, table_name, startDate, endDate):

    # Преобразуем строки в объекты datetime
    start_date_object = datetime.strptime(startDate, '%d.%m.%Y')
    end_date_object = datetime.strptime(endDate, '%d.%m.%Y')

    # Форматируем даты для SQL-запроса с ведущим нулём для дня и месяца
    start_date_formatted = start_date_object.strftime('%Y-%m-%d')
    end_date_formatted = end_date_object.strftime('%Y-%m-%d')

    query = f"""
    SELECT
        COALESCE(SUM(Income_Summ), 0) -
        (COALESCE(SUM(Expenses_Summ), 0) + COALESCE(SUM(Expenses_Summ), 0) * 0.03) -
        COALESCE(SUM(Consumables_Summ), 0) +
        COALESCE(SUM(Returns_Summ), 0) +
        COALESCE(SUM(Garant_Summ), 0) AS TotalProfit
    FROM
        {table_name}
    WHERE Data BETWEEN '{start_date_formatted}' AND '{end_date_formatted}'
    """
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()
    return result['TotalProfit'] if result else 0


def get_total_consumables(conn, table_name, startDate, endDate):

    # Преобразуем строки в объекты datetime
    start_date_object = datetime.strptime(startDate, '%d.%m.%Y')
    end_date_object = datetime.strptime(endDate, '%d.%m.%Y')

    # Форматируем даты для SQL-запроса с ведущим нулём для дня и месяца
    start_date_formatted = start_date_object.strftime('%Y-%m-%d')
    end_date_formatted = end_date_object.strftime('%Y-%m-%d')


    query = f"""
    SELECT
        (COALESCE(SUM(Expenses_Summ), 0) + COALESCE(SUM(Expenses_Summ), 0) * 0.03)+
        COALESCE(SUM(Consumables_Summ), 0)
    AS TotalConsumables
    FROM {table_name}
    WHERE Data BETWEEN '{start_date_formatted}' AND '{end_date_formatted}'
    """
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()
    # Проверка на None и возвращение 0, если результат запроса None
    total_consumables = result[0] if result and result[0] is not None else 0
    return total_consumables



@app.route('/daily_stats', methods=['GET'])
def daily_stats():
    conn = get_db_connection()
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    Selected_user = request.args.get('Selected_user')

    if Selected_user == "all":
        user_tables = get_user_tables(conn)
    else:
        user_tables = [Selected_user]

    daily_stats = get_daily_stats(conn, user_tables, startDate, endDate)
    conn.close()

    return jsonify(daily_stats)





def get_daily_stats(conn, user_tables, startDate, endDate):
    daily_stats = {}

    # Преобразуем входные даты в формат YYYY-MM-DD
    start_date_object = datetime.strptime(startDate, '%d.%m.%Y')
    end_date_object = datetime.strptime(endDate, '%d.%m.%Y')

    start_date_formatted = start_date_object.strftime('%Y-%m-%d')
    end_date_formatted = end_date_object.strftime('%Y-%m-%d')

    for table_name in user_tables:
        cur = conn.cursor()
        query = f"""
        SELECT
            Data AS FormattedDate,
            COALESCE(SUM(Income_Summ), 0) -
            (COALESCE(SUM(Expenses_Summ), 0) + COALESCE(SUM(Expenses_Summ), 0) * 0.03) -
            COALESCE(SUM(Consumables_Summ), 0) +
            COALESCE(SUM(Returns_Summ), 0) AS DailyProfit,
            COALESCE(SUM(Expenses_Summ), 0) + COALESCE(SUM(Expenses_Summ), 0) * 0.03 + COALESCE(SUM(Consumables_Summ), 0) AS DailyExpenses,
            COALESCE(SUM(Income_Summ), 0) AS DailyIncome,
            COALESCE(SUM(Returns_Summ), 0) AS DailyReturns
        FROM
            {table_name}
        WHERE
            Data BETWEEN '{start_date_formatted}' AND '{end_date_formatted}'
        GROUP BY FormattedDate
        ORDER BY FormattedDate
        """
        cur.execute(query)
        results = cur.fetchall()

        for result in results:
            # Дата уже в формате YYYY-MM-DD
            date_str = result['FormattedDate']
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            profit = result['DailyProfit']
            expenses = result['DailyExpenses']
            payout = profit * 0.2  # DailyPayout на основе DailyProfit
            income = result['DailyIncome']
            returns = result['DailyReturns']

            # Преобразуем дату для ключа в формате DD.MM.YYYY
            date_key = date.strftime('%d.%m.%Y')

            if date_key not in daily_stats:
                daily_stats[date_key] = {'profit': 0, 'expenses': 0, 'payout': 0, 'roi': 0, 'income': 0, 'returns': 0}

            daily_stats[date_key]['profit'] += profit
            daily_stats[date_key]['expenses'] += expenses
            daily_stats[date_key]['payout'] += payout
            daily_stats[date_key]['roi'] = (daily_stats[date_key]['profit'] / daily_stats[date_key]['expenses'] * 100) if daily_stats[date_key]['expenses'] else 0
            daily_stats[date_key]['income'] += income
            daily_stats[date_key]['returns'] += returns

    # Сортируем результаты
    sorted_daily_stats = sorted(daily_stats.items(), key=lambda x: datetime.strptime(x[0], '%d.%m.%Y'))

    return [{'date': date, 'profit': daily_stat['profit'], 'expenses': daily_stat['expenses'], 'payout': daily_stat['payout'], 'roi': daily_stat['roi'], 'income': daily_stat['income'], 'returns': daily_stat['returns']} for date, daily_stat in sorted_daily_stats]







@app.route('/get_total', methods=['GET'])
def get_total():
    conn = get_db_connection()
    
    # Получение параметров из строки запроса
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    selected_user = request.args.get('Selected_user')

    user_tables = get_user_tables(conn)
    payouts_data = get_user_payouts(conn, start_date, end_date)

    overall_profit = 0
    overall_consumables = 0
    overall_payout = 0
    table_profits = []

    if selected_user == "all":
        user_tables = get_user_tables(conn)
    else:
        user_tables = [selected_user]
    
    for table_name in user_tables:
        profit = get_total_profit(conn, table_name, start_date, end_date)
        consumables = get_total_consumables(conn, table_name, start_date, end_date)
        overall_profit += profit
        overall_consumables += consumables

        # Расчет выплаты для текущего пользователя
        for payout_id, payout_info in payouts_data.items():
            if payout_info['user'] == table_name:
                contract_salary_percent = payout_info.get('contract_salary_percent', 0) or 0
                contract_salary_usd = payout_info.get('contract_salary_usd', 0) or 0
                # Получение выплаты для текущего пользователя
                user_payout = recalculate_and_update_payouts(conn, table_name, start_date, end_date)

                # Учет выплаты в общей сумме
                overall_payout += user_payout

        table_profits.append({
            'table_name': table_name,
            'profit': f"{profit:.2f}"
        })

    overall_ROI = (overall_profit / overall_consumables) * 100 if overall_consumables else 0
    overall_ROI = f"{overall_ROI:.2f}"
    overall_payout = f"{overall_payout:.2f}"
    overall_profit = f"{overall_profit:.2f}"
    overall_consumables = f"{overall_consumables:.2f}"
    conn.close()

    return jsonify({
        'total_profit': overall_profit,
        'total_consumables': overall_consumables,
        'total_ROI': overall_ROI,
        'total_payout': overall_payout,
        'table_profits': table_profits
    })




@app.route('/get_users_with_payouts', methods=['GET'])
def get_users_with_payouts():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    conn = get_db_connection()
    try:
        users = get_users(conn)
        payouts = get_user_payouts(conn, start_date, end_date)
        return jsonify({'users': users, 'payouts': payouts})
    except Exception as e:
        app.logger.error(f"Error in get_users_with_payouts: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()


@app.route('/delete_user_in_payouts', methods=['POST'])
def delete_user_in_payouts():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем имя пользователя из тела запроса
    data = request.get_json()
    user_to_delete = data.get('user')

    if not user_to_delete:
        conn.close()
        return jsonify({'status': 'error', 'message': 'User parameter is required'}), 400

    try:
        # Удаление пользователя из таблицы
        query = "DELETE FROM users_for_payout WHERE user = ?"
        cur.execute(query, (user_to_delete,))
        conn.commit()

        # Проверка, была ли удалена запись
        if cur.rowcount > 0:
            result = {'status': 'success', 'message': f'User {user_to_delete} was deleted successfully'}
        else:
            result = {'status': 'error', 'message': f'User {user_to_delete} not found'}

    except Exception as e:
        app.logger.error(f"Error deleting user: {e}")
        result = {'status': 'error', 'message': str(e)}
    finally:
        conn.close()

    return jsonify(result)


def get_user_payouts(conn, start_date, end_date):
    create_payouts_table(conn)
    
    # Извлечение месяца и года из start_date
    start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
    month = start_date_obj.month
    year = start_date_obj.year

    query = """
    SELECT id, user, contract_salary_usd, contract_salary_percent, advance, buyer_debt, kpi_salary, fine, bonus, desired_percentage, paid, total, owes_company, comment
    FROM payouts
    WHERE month = ? AND year = ?
    """
    cur = conn.cursor()
    cur.execute(query, (month, year))
    payouts = cur.fetchall()
    payouts_dict = {row['id']: {
        'user': row['user'],
        'contract_salary_usd': row['contract_salary_usd'],
        'contract_salary_percent': row['contract_salary_percent'],
        'advance': row['advance'],
        'buyer_debt': row['buyer_debt'],
        'kpi_salary': row['kpi_salary'],
        'fine': row['fine'],
        'bonus': row['bonus'],
        'desired_percentage': row['desired_percentage'],
        'paid': row['paid'],
        'total': row['total'],
        'owes_company': row['owes_company'],
        'comment': row['comment']
    } for row in payouts}
    return payouts_dict








@app.route('/get_user_payouts_zp', methods=['GET'])
def get_user_payouts_zp():
    conn = get_db_connection()
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    selected_user = request.args.get('Selected_user')

    if selected_user == "all":
        user_tables = get_user_tables(conn)
    else:
        user_tables = [selected_user]
    
    # Извлечение месяца и года из start_date
    start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
    month = start_date_obj.month
    year = start_date_obj.year

    query = """
    SELECT id, user, total
    FROM payouts
    WHERE month = ? AND year = ? AND user IN ({})
    """.format(','.join('?' for _ in user_tables))
    cur = conn.cursor()
    cur.execute(query, (month, year, *user_tables))
    payouts = cur.fetchall()

    if selected_user == "all":
        # Суммируем, заменяя None на 0
        payout_zp = sum(row['total'] or 0 for row in payouts)
        payout_zp = round(payout_zp, 2)
        result = {'payout_zp': payout_zp}
    else:
        payouts_zp = {row['id']: {
            'user': row['user'],
            'total': row['total'] or 0  # Заменяем None на 0
        } for row in payouts}
        result = payouts_zp
    conn.close()
    return jsonify(result)




def update_user_payout(conn, user, start_date, end_date, total):
    # Извлечение месяца и года из start_date и end_date
    start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
    end_date_obj = datetime.strptime(end_date, '%d.%m.%Y')
    month_start = start_date_obj.month
    year_start = start_date_obj.year
    month_end = end_date_obj.month
    year_end = end_date_obj.year

    # Обновляем значение total в базе данных
    query = """
    UPDATE payouts
    SET total = ?
    WHERE user = ? AND 
    (year > ? OR (year = ? AND month >= ?)) AND 
    (year < ? OR (year = ? AND month <= ?))
    """
    
    cur = conn.cursor()
    cur.execute(query, (total, user, year_start, year_start, month_start, year_end, year_end, month_end))
    conn.commit()

    # Проверка количества затронутых строк
    rows_affected = cur.rowcount
    return rows_affected





@app.route('/calculate_and_update_payout', methods=['POST'])
def calculate_and_update_payout():
    conn = get_db_connection()
    data = request.get_json()

    # Получаем параметры из запроса
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    user = data.get('user')

    # Проверяем, что параметры переданы
    if not start_date or not end_date or not user:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400

    try:
        # Вызываем функцию пересчета и обновления
        total_salary = recalculate_and_update_payouts(conn, user, start_date, end_date)
        total_salary = f"{total_salary:.2f}"
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    conn.close()
    
    # Формируем ответ
    return jsonify({'status': 'success', 'total_salary': total_salary})









def recalculate_and_update_payouts(conn, user, start_date, end_date):
    # Преобразование дат
    start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
    end_date_obj = datetime.strptime(end_date, '%d.%m.%Y')
    month_start = start_date_obj.month
    year_start = start_date_obj.year
    month_end = end_date_obj.month
    year_end = end_date_obj.year

    cur = conn.cursor()

    # Выбор данных для каждого месяца в диапазоне
    query = """
    SELECT year, month, contract_salary_usd, contract_salary_percent, advance, buyer_debt, fine, bonus, kpi_salary
    FROM payouts
    WHERE user = ? AND 
    (year > ? OR (year = ? AND month >= ?)) AND 
    (year < ? OR (year = ? AND month <= ?))
    """
    cur.execute(query, (user, year_start, year_start, month_start, year_end, year_end, month_end))
    payouts = cur.fetchall()

    if not payouts:
        return 0  # Если данных нет, возвращаем 0

    total_salary_sum = 0

    # Пересчет для каждого месяца
    for payout in payouts:
        contract_salary_usd = payout['contract_salary_usd'] or 0
        contract_salary_percent = payout['contract_salary_percent'] or 0
        advance = payout['advance'] or 0
        buyer_debt = payout['buyer_debt'] or 0
        fine = payout['fine'] or 0
        bonus = payout['bonus'] or 0
        kpi_salary = payout['kpi_salary'] or 0

        # Рассчитываем профит для текущего месяца
        current_start_date = f"01.{payout['month']:02d}.{payout['year']}"
        current_end_date = f"{calendar.monthrange(payout['year'], payout['month'])[1]:02d}.{payout['month']:02d}.{payout['year']}"
        total_profit = get_total_profit(conn, user, current_start_date, current_end_date)

        # Рассчитываем итоговую сумму
        total_salary = (contract_salary_usd * kpi_salary + contract_salary_percent * total_profit) - advance - buyer_debt - fine + bonus

        # Обновляем данные
        update_query = """
        UPDATE payouts
        SET total = ?
        WHERE user = ? AND year = ? AND month = ?
        """
        cur.execute(update_query, (total_salary, user, payout['year'], payout['month']))

        # Суммируем общую зарплату
        total_salary_sum += total_salary

    # Коммит изменений в базе
    conn.commit()

    if total_salary_sum  < 0:
        return 0
    

    return total_salary_sum











@app.route('/save_user_payouts', methods=['POST'])
def save_user_payouts():
    conn = get_db_connection()
    create_payouts_table(conn)
    cur = conn.cursor()

    payouts = request.json  # Получаем данные в формате JSON
    start_date = payouts.pop('startDate')
    end_date = payouts.pop('endDate')

    # Извлечение месяца и года из start_date
    start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
    month = start_date_obj.month
    year = start_date_obj.year

    for user, fields in payouts.items():
        # Проверка существования записи
        cur.execute("SELECT id FROM payouts WHERE user = ? AND month = ? AND year = ?", (user, month, year))
        result = cur.fetchone()

        if result:
            query = """
            UPDATE payouts SET
                contract_salary_usd = COALESCE(?, contract_salary_usd),
                contract_salary_percent = COALESCE(?, contract_salary_percent),
                advance = COALESCE(?, advance),
                buyer_debt = COALESCE(?, buyer_debt),
                kpi_salary = COALESCE(?, kpi_salary),
                fine = COALESCE(?, fine),
                bonus = COALESCE(?, bonus),
                desired_percentage = COALESCE(?, desired_percentage),
                paid = COALESCE(?, paid),
                total = COALESCE(?, total),
                owes_company = COALESCE(?, owes_company),
                comment = COALESCE(?, comment)
            WHERE id = ?
            """
            cur.execute(query, (
                fields.get('contract_salary_usd') or 0,
                fields.get('contract_salary_percent') or 0,
                fields.get('advance') or 0,
                fields.get('buyer_debt') or 0,
                fields.get('kpi_salary') or 0,
                fields.get('fine') or 0,
                fields.get('bonus') or 0,
                fields.get('desired_percentage') or 0,
                fields.get('paid') or 0,
                fields.get('total') or 0,
                fields.get('owes_company') or 0,
                fields.get('comment') or '',  # Для текстовых полей можно оставить пустую строку
                result['id']
            ))
        else:
            query = """
            INSERT INTO payouts (user, contract_salary_usd, contract_salary_percent, advance, buyer_debt, kpi_salary, fine, bonus, desired_percentage, paid, total, owes_company, comment, month, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(query, (
                user,
                fields.get('contract_salary_usd') or 0,
                fields.get('contract_salary_percent') or 0,
                fields.get('advance') or 0,
                fields.get('buyer_debt') or 0,
                fields.get('kpi_salary') or 0,
                fields.get('fine') or 0,
                fields.get('bonus') or 0,
                fields.get('desired_percentage') or 0,
                fields.get('paid') or 0,
                fields.get('total') or 0,
                fields.get('owes_company') or 0,
                fields.get('comment') or '',  # Для текстовых полей можно оставить пустую строку
                month,
                year
            ))

    conn.commit()
    conn.close()
    return jsonify({'success': True})




def get_users(conn):
    create_user_table(conn)
    query = "SELECT user FROM users_for_payout"
    cur = conn.cursor()
    cur.execute(query)
    users = cur.fetchall()
    return [user[0] for user in users]


@app.route('/admin/payout')
def admin_payout():


    conn = get_db_connection()
    create_user_table(conn)
    conn.close()

    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin_payout.html')

@app.route('/payout')
def admin_payout2():


    conn = get_db_connection()
    create_user_table(conn)
    conn.close()

    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin_payout.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    conn = get_db_connection()
    create_user_table(conn)
    user = request.form.get('user')
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users_for_payout (user) VALUES (?)", (user,))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()
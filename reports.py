from imporst import *
from creations import *
from keys_and_tokens import *

from flask import send_file, request, jsonify
from io import BytesIO
from datetime import datetime
import pandas as pd
import sqlite3
import os

@app.route('/generate_leads_report', methods=['GET'])
def export_leads_report():
    try:
        role = 'admin'
        if role != 'admin':
            return jsonify({"success": False, "message": "Требуются права администратора"}), 403

        start_date = request.args.get("start")
        end_date = request.args.get("end")
        username = request.args.get("username", "all")

        start_sql = f"{start_date} 00:00:00" if start_date else None
        end_sql = f"{end_date} 23:59:59" if end_date else None

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                leads.id,
                leads.user_id,
                users.login AS username,
                leads.status,
                leads.distributor_payout,
                leads.subid,
                leads.datatime,
                leads.userip,
                leads.firstname,
                leads.lastname,
                leads.email,
                leads.phone,
                leads.funnel,
                leads.advertiser_id,
                leads.campaign_id,
                leads.campaign_name,
                leads.banner_id,
                leads.geo AS city_id,
                leads.gender,
                leads.age,
                leads.random,
                leads.impression_weekday AS day_of_week,
                leads.impression_hour AS hour,
                leads.user_timezone AS timezone,
                leads.search_phrase AS keyword,
                leads.utm_source,
                leads.utm_medium,
                leads.source AS utm_campaign,
                leads.device_type AS device,
                leads.position
            FROM leads
            JOIN users ON leads.user_id = users.user_id
            WHERE 1=1
        """
        params = []

        if username != "all":
            query += " AND users.login = ?"
            params.append(username)

        if start_sql:
            query += " AND leads.datatime >= ?"
            params.append(start_sql)
        if end_sql:
            query += " AND leads.datatime <= ?"
            params.append(end_sql)

        query += " ORDER BY leads.datatime DESC"

        cursor.execute(query, params)
        leads = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(leads, columns=columns)

        if df.empty:
            return jsonify({"success": False, "message": "Нет данных для экспорта"}), 404

        # Русские названия колонок
        rename_columns = {
            'id': 'ID',
            'user_id': 'ID пользователя',
            'username': 'Имя пользователя',
            'status': 'Статус',
            'distributor_payout': 'Выплата дистрибьютору',
            'subid': 'SubID',
            'datatime': 'Дата и время',
            'userip': 'IP пользователя',
            'firstname': 'Имя',
            'lastname': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'funnel': 'Воронка',
            'advertiser_id': 'ID рекламодателя',
            'campaign_id': 'ID кампании',
            'campaign_name': 'Название кампании',
            'banner_id': 'ID баннера',
            'city_id': 'Регион',
            'gender': 'Пол',
            'age': 'Возраст',
            'random': 'Случайное число',
            'day_of_week': 'День недели',
            'hour': 'Час',
            'timezone': 'Часовой пояс',
            'keyword': 'Поисковая фраза',
            'utm_source': 'Источник трафика',
            'utm_medium': 'Тип трафика',
            'utm_campaign': 'UTM-кампания',
            'device': 'Тип устройства',
            'position': 'Позиция объявления'
        }
        df.rename(columns=rename_columns, inplace=True)

        params_df = pd.DataFrame([{
            "Параметр": "Период",
            "Значение": f"с {start_date or 'начала'} по {end_date or 'конец'}"
        }, {
            "Параметр": "Пользователь",
            "Значение": username
        }])

        total_leads = len(df)
        total_sales = len(df[df['Статус'] == 'sale'])
        total_payout = df[df['Статус'] == 'sale']['Выплата дистрибьютору'].sum()
        summary_df = pd.DataFrame([{
            "Всего лидов": total_leads,
            "Всего продаж": total_sales,
            "Сумма выплат": round(total_payout, 2),
            "Конверсия (%)": round((total_sales / total_leads) * 100, 2) if total_leads else 0
        }])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            params_df.to_excel(writer, index=False, sheet_name="Отчет", startrow=0)
            df.to_excel(writer, index=False, sheet_name="Отчет", startrow=len(params_df) + 2)
            summary_df.to_excel(writer, index=False, sheet_name="Отчет", startrow=len(df) + len(params_df) + 4)

            workbook = writer.book
            worksheet = writer.sheets['Отчет']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(len(params_df) + 2, col_num, value, header_format)

        output.seek(0)
        return send_file(
            output,
            download_name=f"leads_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка генерации отчета: {str(e)}"}), 500


@app.route('/generate_agent_report', methods=['GET'])
def generate_agent_report():
    try:
        username = request.args.get("username")
        start_date_str = request.args.get('start_date')  # формат: ДД.ММ.ГГГГ
        end_date_str = request.args.get('end_date')

        if not username or not start_date_str or not end_date_str:
            return jsonify({
                "success": False,
                "message": "Параметры 'username', 'start_date', 'end_date' обязательны"
            }), 400

        # Преобразуем строки в datetime
        start_date_obj = datetime.strptime(start_date_str, "%d.%m.%Y")
        end_date_obj = datetime.strptime(end_date_str, "%d.%m.%Y")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем user_id
        cursor.execute("SELECT user_id FROM users WHERE login = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"success": False, "message": "Пользователь не найден"}), 404
        user_id = user["user_id"]

        # Получаем данные компании
        cursor.execute("SELECT * FROM distributors_info WHERE user_id = ?", (user_id,))
        company = cursor.fetchone()
        if not company:
            return jsonify({"success": False, "message": "Информация о компании не найдена"}), 404

        # Получаем статистику по лидам
        cursor.execute("""
            SELECT COUNT(*) as total_leads,
                   SUM(CASE WHEN status = 'sale' THEN 1 ELSE 0 END) as total_sales,
                   SUM(CASE WHEN status = 'sale' THEN distributor_payout ELSE 0 END) as total_payout
            FROM leads
            WHERE user_id = ? AND datatime BETWEEN ? AND ?
        """, (
            user_id,
            start_date_obj.strftime('%Y-%m-%d 00:00:00'),
            end_date_obj.strftime('%Y-%m-%d 23:59:59')
        ))
        stats = cursor.fetchone()

        total_leads = stats['total_leads'] or 0
        total_sales = stats['total_sales'] or 0
        total_payout = float(stats['total_payout']) if stats['total_payout'] else 0.0

        today = datetime.today()

        # Генерация Word-документа
        doc = Document()

        # Заголовок справа
        for text in [
            "Приложение № _____",
            "к агентскому договору на реализацию товара",
            f"№ _____ от __.__.20__ г."
        ]:
            p = doc.add_paragraph(text)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            p.runs[0].font.size = Pt(12)

        doc.add_paragraph()

        title = doc.add_paragraph("Отчет о выполнении поручения")
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        title.runs[0].bold = True

        doc.add_paragraph(f"г. {today.year}")
        doc.add_paragraph(f"Агент: {company['company_name']}")
        doc.add_paragraph(f"Агентский договор на реализацию товара № _____ от __.__.20__ г.")
        doc.add_paragraph(f"Отчетный период: {start_date_obj.strftime('%m.%Y')} (месяц, год)")

        doc.add_paragraph("1. За отчетный период Агентом совершены следующие фактические действия:")

        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Действие'
        hdr_cells[1].text = 'Дата совершения'

        row_cells = table.add_row().cells
        row_cells[0].text = f"Передано заявок: {total_leads}"
        row_cells[1].text = f"{start_date_obj.strftime('%d.%m.%Y')} — {end_date_obj.strftime('%d.%m.%Y')}"

        doc.add_paragraph("")
        doc.add_paragraph(
            f"2. За отчетный период Агентом были предоставлены {total_leads} заявок в период с "
            f"{start_date_obj.strftime('%d.%m.%Y')} по {end_date_obj.strftime('%d.%m.%Y')}, "
            f"из них {total_sales} продаж(и), по которым агенту полагается выплата в размере "
            f"{round(total_payout, 2)} ₽."
        )

        output = BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f"agent_report_{username}_{today.strftime('%Y%m%d')}.docx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка генерации отчета: {str(e)}"}), 500

from imporst import *
from keys_and_tokens import *
# from profit import *
from creations import *
from goals import *
from dashboard import *
from dashboard2 import *
from users import *
from notifications import *
from leads import *






scheduler.start()

# scheduler.add_job(
#     id='delete_old_leads',
#     func=delete_old_leads,
#     trigger='cron',  # Запуск по расписанию
#     hour=0,  # Каждый день в полночь
#     minute=0,
#     replace_existing=True
# )

scheduler.add_job(
    id='transfer_previous_month_data',  # Уникальный идентификатор задачи
    func=transfer_previous_month_data,  # Функция, которая будет выполняться
    trigger='cron',         # Запуск по расписанию
    day=1,                 # Первое число каждого месяца
    hour=0,                # В 00:00
    minute=0,              # В 00:00
    replace_existing=True  # Заменить существующую задачу с таким же ID
)

# Добавляем задачу на запуск функции fetch_conversions_log каждые 10 минут
# scheduler.add_job(
#     id='fetch_conversions_log',
#     func=fetch_conversions_log,
#     trigger='interval',  # Запуск через определенный интервал
#     minutes=10,  # Каждые 10 минут
#     replace_existing=True
# )


# Старт приложения
if __name__ == "__main__":
    
    


    conn = get_db_connection()
    # Сначала создаем независимые таблицы
    create_users_table_if_not_exists(conn)          # Таблица users (базовая для многих внешних ключей)
    create_roles_table_if_not_exists(conn)          # Таблица roles
    create_pages_table_if_not_exists(conn)          # Таблица pages
    create_notifications_table_if_not_exists(conn)  # Таблица notifications

    # Затем создаем таблицы с зависимостями
    create_avatars_table_if_not_exists(conn) 
    create_employers_table_if_not_exists(conn)      # Зависит от users
    create_role_pages_table_if_not_exists(conn)     # Зависит от roles и pages
    create_notification_users_table_if_not_exists(conn)  # Зависит от notifications и users
    create_leads_table_if_not_exists(conn)          # Зависит от users
    create_blacklist_leads_table_if_not_exists(conn)     # Независимая
    create_api_antidubl_blackout_logs_table_if_not_exists(conn)  # Независимая
    create_whatsapp_templates_table_if_not_exists(conn)  # Зависит от users
    create_wa_api_logs_table_if_not_exists(conn)
    create_email_templates_table_if_not_exists(conn)     # Независимая (опционально зависит от users)
    create_email_api_logs_table_if_not_exists(conn)
    create_goals_table_if_not_exists(conn) 

    conn.close()





    # Запускаем Flask-приложение
    app.run(debug=True)
    
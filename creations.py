from imporst import *



app = Flask(__name__, static_folder='static')
app.secret_key = '123'

CORS(app, supports_credentials=True)

# Настройка для Flask-APScheduler
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Novosibirsk'


scheduler = APScheduler()
scheduler.init_app(app)



def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    
    return conn





def create_users_table_if_not_exists(conn):
    query = """
    CREATE TABLE IF NOT EXISTS users (
        "login"	TEXT NOT NULL UNIQUE,
        "pass"	TEXT NOT NULL,
        "user_id"	INTEGER,
        "avatar_path" TEXT NOT NULL,
        PRIMARY KEY("user_id" AUTOINCREMENT)
    )
    """
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()





def create_goals_table_if_not_exists(conn):
    query = """
    CREATE TABLE IF NOT EXISTS goals (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "Data" TEXT NOT NULL,              -- формат: MM.YYYY
        "Name" TEXT NOT NULL,              -- имя пользователя
        "Profit" REAL NOT NULL             -- целевое значение
    )
    """
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def create_roles_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "roles" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "name" TEXT NOT NULL
            );
        """)





def create_pages_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "pages" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "url" TEXT NOT NULL
            );
        """)


def create_role_pages_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "role_pages" (
            "role_id" INTEGER NOT NULL,
            "page_id" INTEGER NOT NULL,
            FOREIGN KEY("role_id") REFERENCES "roles"("id"),
            FOREIGN KEY("page_id") REFERENCES "pages"("id"),
            PRIMARY KEY("role_id", "page_id")
            );
        """)






#Уведомления
def create_notifications_table_if_not_exists(conn):
    with conn:
        conn.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    url TEXT
);

        """)


def create_notification_users_table_if_not_exists(conn):
    with conn:
        conn.execute("""
CREATE TABLE IF NOT EXISTS notification_users (
    notification_id INTEGER,
    user_id INTEGER,
    isReaded BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (notification_id, user_id),
    FOREIGN KEY (notification_id) REFERENCES notifications(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

        """)




def create_leads_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status INTEGER NOT NULL,
                distributor_payout INTEGER DEFAULT 0,
                subid TEXT NOT NULL,
                datatime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                userip TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                funnel TEXT NOT NULL,
                advertiser_id TEXT,           -- ID рекламодателя (только ВК)
                campaign_id TEXT,             -- ID кампании (ВК: {{campaign_id}}, Яндекс: {campaign_id})
                campaign_name TEXT,           -- Название кампании (ВК: {{campaign_name}}, Яндекс: utm_campaign)
                banner_id TEXT,               -- ID баннера/объявления (ВК: {{banner_id}}, Яндекс: {ad_id})
                geo TEXT,                     -- ID региона (ВК: {{geo}}, Яндекс: {region_id})
                gender TEXT,                  -- Пол пользователя (только ВК: {{gender}})
                age TEXT,                     -- Возраст пользователя (только ВК: {{age}})
                random TEXT,                  -- Случайное число (ВК: {{random}}, Яндекс: {random})
                impression_weekday TEXT,      -- День недели показа (только ВК: {{impression_weekday}})
                impression_hour TEXT,         -- Час показа (только ВК: {{impression_hour}})
                user_timezone TEXT,           -- Часовой пояс (только ВК: {{user_timezone}})
                search_phrase TEXT,           -- Поисковый запрос (ВК: {{search_phrase}}, Яндекс: utm_term)
                utm_source TEXT,              -- Источник трафика (Яндекс: utm_source)
                utm_medium TEXT,              -- Тип трафика (Яндекс: utm_medium)
                source TEXT,                  -- Площадка размещения (Яндекс: {source})
                device_type TEXT,             -- Тип устройства (Яндекс: {device_type})
                position TEXT,                -- Позиция объявления (Яндекс: {position})
                FOREIGN KEY("user_id") REFERENCES "users"("user_id")
            );
        """)

        # Получаем список существующих столбцов
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(leads)")
        existing_columns = {row[1] for row in cursor.fetchall()}  # row[1] - название столбца

        # Определяем недостающие столбцы (kt_sub_id_1 ... kt_sub_id_10)
        new_columns = {}
        for i in range(1, 11):
            new_columns[f"kt_sub_id_{i}"] = "TEXT"

        # Добавляем недостающие столбцы
        for column, data_type in new_columns.items():
            if column not in existing_columns:
                alter_query = f"ALTER TABLE leads ADD COLUMN {column} {data_type};"
                conn.execute(alter_query)





def create_blacklist_leads_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userip TEXT UNIQUE,
                email TEXT UNIQUE,
                reason TEXT,
                source TEXT CHECK(source IN ('auto', 'manual')),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 🔥 Индексы для быстрого поиска в блэклисте
        conn.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_userip ON leads_blacklist(userip)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_email ON leads_blacklist(email)")

def create_api_antidubl_blackout_logs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads_api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_ip TEXT,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 🔥 Индекс для быстрого поиска по IP в логах
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_request_ip ON leads_api_logs(request_ip)")






def create_whatsapp_templates_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

def create_wa_api_logs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wa_api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_payload TEXT NOT NULL,
                response_payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)



def create_email_templates_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_templates (
                user_id INTEGER PRIMARY KEY ,
                template_name TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id)
            );


        """)



def create_email_api_logs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipient_email TEXT NOT NULL,
                template_name TEXT NOT NULL,
                send_status TEXT NOT NULL CHECK (send_status IN ('success', 'failure')),
                error_message TEXT,
                transaction_id TEXT,
                message_id TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)








def create_distributors_info_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS distributors_info (
                user_id INTEGER PRIMARY KEY,        -- внешний и первичный ключ
                company_name TEXT NOT NULL,
                description TEXT,
                website TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                image_path TEXT,                    -- путь к изображению (например, логотипу)
                contract_start_date DATE,           -- дата начала договора
                ogrn TEXT,                          -- ОГРН
                inn TEXT,                           -- ИНН
                kpp TEXT,                           -- КПП
                bank_account TEXT,                  -- Р/с
                bank_name TEXT,                     -- Банк
                correspondent_account TEXT,         -- К/с
                bik TEXT,                           -- БИК
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        # Индексы (по ключевым бизнес-полям)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON distributors_info(company_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_company_website ON distributors_info(website)")


























def get_user_tables(conn):
    query = "SELECT login FROM users WHERE login != 'admin'"
    cur = conn.cursor()
    cur.execute(query)
    tables = cur.fetchall()
    user_tables = [table[0] for table in tables if table[0] and table[0].lower() != 'admin']  # Дополнительная проверка
    return user_tables


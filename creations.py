from imporst import *



app = Flask(__name__, static_folder='static')
app.secret_key = '123'

CORS(app, supports_credentials=True)

# Настройка для Flask-APScheduler
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Novosibirsk '


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
        PRIMARY KEY("user_id" AUTOINCREMENT)
    )
    """
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def create_avatars_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS avatars (
                user_id INTEGER,
                avatar_path TEXT NOT NULL,
                PRIMARY KEY (user_id)
            );
        """)




def create_employers_table_if_not_exists(conn):
    query = """
    CREATE TABLE IF NOT EXISTS employers (
        "name"	TEXT NOT NULL UNIQUE,
        "surname"	TEXT NOT NULL,
        "date_of_hiring" DATETIME
        "email"	TEXT NOT NULL,
        "phone"	TEXT NOT NULL,
        "user_id" INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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

































def get_user_tables(conn):
    query = "SELECT login FROM users WHERE login != 'admin'"
    cur = conn.cursor()
    cur.execute(query)
    tables = cur.fetchall()
    user_tables = [table[0] for table in tables if table[0] and table[0].lower() != 'admin']  # Дополнительная проверка
    return user_tables



def create_user_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS users_for_payout (
        user TEXT PRIMARY KEY
    )
    """
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def create_payouts_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS payouts (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "user" TEXT,
        "contract_salary_usd" INTEGER,
        "contract_salary_percent" INTEGER,
        "advance" INTEGER,
        "buyer_debt" INTEGER,
        "kpi_salary" INTEGER,
        "fine" INTEGER,
        "bonus" INTEGER,
        "desired_percentage" INTEGER,
        "paid" INTEGER,
        "total" INTEGER,
        "owes_company" INTEGER,
        "comment" TEXT,
        "month" INTEGER,
        "year" INTEGER
    )
    """
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def create_pixel_log_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pixel_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            account_id TEXT,
            offer_id TEXT,
            status TEXT,
            business TEXT,
            access_token TEXT
        )
    ''')
    conn.commit()
    conn.close()











#accounting
def create_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS proliv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            payer TEXT NOT NULL,
            amount_usd REAL,
            amount_rub REAL,
            note TEXT,
            category TEXT
        );
        """)

def create_categories_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """)

def create_pp_names_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pp_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """)



def create_conversion_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            rate REAL NOT NULL,
            total_rub REAL NOT NULL,
            total_usd REAL NOT NULL,
            payer TEXT,
            category TEXT,
            note TEXT
        );
        """)


def create_pp_crypt_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pp_crypt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            amount_usd REAL NOT NULL
        );
        """)


def create_expenses_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            client TEXT NOT NULL,
            amount_usd REAL NOT NULL,
            comment TEXT,
            note TEXT
        );
        """)

def create_expenses_user_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            client TEXT NOT NULL,
            amount_usd REAL NOT NULL,
            comment TEXT,
            note TEXT
        );
        """)

def create_clients_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """)

def create_fixed_costs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS fixed_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cost REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL
        );
        """)

def create_variable_costs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS variable_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cost REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL
        );
        """)





#crm
def create_table_for_tablenames_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tablenames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_table_name TEXT NOT NULL,
                user_table_name TEXT NOT NULL,
                hidden BOOLEAN NOT NULL,
                username TEXT NOT NULL 
            );
        """)


def create_table_for_columns_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_table_name TEXT NOT NULL,
                column_name TEXT NOT NULL,
                column_type TEXT NOT NULL
            );
        """)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(columns)")
        columns = [info[1] for info in cursor.fetchall()]  # Получаем список имен столбцов
        if 'column_key' not in columns:
            cursor.execute('ALTER TABLE columns ADD COLUMN column_key TEXT')



def create_access_table_if_not_exists(conn):
    with conn:
        # Создаем таблицу, если она не существует
        conn.execute("""
            CREATE TABLE IF NOT EXISTS table_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_table_name TEXT NOT NULL,
                username TEXT NOT NULL
            );
        """)

        cursor = conn.cursor()
        # Проверяем, существует ли столбец 'access'
        cursor.execute("PRAGMA table_info(table_access)")
        columns = [info[1] for info in cursor.fetchall()]  # Получаем список имен столбцов

        if 'access' not in columns:
            # Добавляем столбец 'access', если он не существует
            cursor.execute('ALTER TABLE table_access ADD COLUMN access TEXT')
            # Устанавливаем значение 'editor' для всех строк, где 'access' пустое
            cursor.execute("UPDATE table_access SET access = 'editor' WHERE access IS NULL")
        
        conn.commit()  # Подтверждаем изменения



def create_formul_for_columns_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS formuls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_table_name TEXT NOT NULL,
                column_name TEXT NOT NULL,
                formula TEXT NOT NULL,
                UNIQUE(db_table_name, column_name)
            );
        """)



def create_options_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS options_in_table_crm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_table_name TEXT NOT NULL,
                column_name TEXT NOT NULL,
                option TEXT NOT NULL,
                UNIQUE(db_table_name, column_name, option)
            );
        """)








#calendar
# Создание таблицы дней для календаря, если не существует
def create_days_for_calendar_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS days (
                day_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                UNIQUE(date)
            );
        """)

# Создание таблицы типов заметок, если не существует
def create_notetypes_for_calendar_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notetypes (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                typename TEXT NOT NULL,
                UNIQUE(typename)
            );
        """)

# Создание таблицы заметок, если не существует
def create_notes_for_calendar_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_id INTEGER NOT NULL,
                type_id INTEGER NOT NULL,
                title TEXT,
                description TEXT,
                notes TEXT,
                created_by TEXT NOT NULL,  -- Новая колонка для создателя
                is_public BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (day_id) REFERENCES days(day_id),
                FOREIGN KEY (type_id) REFERENCES notetypes(type_id),
                FOREIGN KEY (created_by) REFERENCES users(login)
            );
        """)

    # Проверяем наличие новых столбцов
    with conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notes)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'created_by' not in columns:
            cursor.execute('ALTER TABLE notes ADD COLUMN created_by TEXT NOT NULL DEFAULT ""')


# Создание таблицы участников заметок, если не существует
def create_note_participants_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS note_participants (
                note_id INTEGER NOT NULL,
                user_login TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(note_id),
                FOREIGN KEY (user_login) REFERENCES users(login),
                PRIMARY KEY (note_id, user_login)
            );
        """)

# Создание таблицы митапов, если не существует
def create_meetups_table_if_not_exists(conn):
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetups (
                meetup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meetup_date TEXT NOT NULL,
                meetup_time TEXT NOT NULL,
                meetup_topic TEXT
            );
        """)

        # Проверяем наличие столбца 'created_by'
        cursor.execute("PRAGMA table_info(meetups)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'created_by' not in columns:
            # Добавляем столбец 'created_by' с дефолтным значением 'unknown'
            cursor.execute("ALTER TABLE meetups ADD COLUMN created_by TEXT NOT NULL DEFAULT ''")



# Создание таблицы участников митапов, если не существует
def create_meetup_participants_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meetup_participants (
                meetup_id INTEGER NOT NULL,
                user_login TEXT NOT NULL,
                FOREIGN KEY (meetup_id) REFERENCES meetups(meetup_id),
                FOREIGN KEY (user_login) REFERENCES users(login),
                PRIMARY KEY (meetup_id, user_login)
            );
        """)

# Создание таблицы вопросов для митапов, если не существует
def create_meetup_questions_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meetup_questions (
                meetup_id INTEGER NOT NULL,
                meetup_question TEXT NOT NULL,
                FOREIGN KEY (meetup_id) REFERENCES meetups(meetup_id)
            );
        """)

# Создание таблицы ответов для митапов, если не существует
def create_meetup_answers_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meetup_answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meetup_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY (meetup_id) REFERENCES meetups(meetup_id)
            );
        """)











def create_roles_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "roles" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "name" TEXT NOT NULL
            );
        """)


def create_user_roles_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "user_roles" (
            "user_id" INTEGER NOT NULL,
            "role_id" INTEGER NOT NULL,
            FOREIGN KEY("user_id") REFERENCES "users"("id"),
            FOREIGN KEY("role_id") REFERENCES "roles"("id"),
            PRIMARY KEY("user_id", "role_id")
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


def create_user_pages_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "user_pages" (
            "user_id" INTEGER NOT NULL,
            "page_id" INTEGER NOT NULL,
            FOREIGN KEY("user_id") REFERENCES "users"("id"),
            FOREIGN KEY("page_id") REFERENCES "pages"("id"),
            PRIMARY KEY("user_id", "page_id")
            );
        """)







#Посты
def create_social_networks_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS SocialNetworks (
                network_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255)
            );
        """)

def create_accounts_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                network_id INTEGER,
                login VARCHAR(255),
                password VARCHAR(255),
                link VARCHAR(255),
                email VARCHAR(255),
                account_name VARCHAR(255),
                access_token TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (network_id) REFERENCES SocialNetworks(network_id)
            );
        """)

def create_fpages_table_if_not_exists(conn):
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FPages (
                page_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                fb_page_id VARCHAR(255),
                page_name VARCHAR(255),
                FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
            );
        """)
        # Проверяем наличие столбца 'created_by'
        cursor.execute("PRAGMA table_info(FPages)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'fp_access_token' not in columns:
            # Добавляем столбец 'created_by' с дефолтным значением 'unknown'
            cursor.execute("ALTER TABLE FPages ADD COLUMN fp_access_token TEXT NOT NULL DEFAULT ''")



def create_posts_table_if_not_exists(conn):
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Posts (
                post_id TEXT TEGER PRIMARY KEY,
                user_id INTEGER,
                account_id INTEGER,
                page_id INTEGER,
                content TEXT,
                image_url VARCHAR(255),
                video_url VARCHAR(255),
                post_url VARCHAR(255),
                scheduled_time DATETIME,
                content_type TEXT CHECK(content_type IN ('text', 'image', 'video', 'link')),
                status TEXT CHECK(status IN ('scheduled', 'posted', 'failed', 'in_progress', 'retrying')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (account_id) REFERENCES Accounts(account_id),
                FOREIGN KEY (page_id) REFERENCES FPages(page_id)
            );
        """)



def create_post_history_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PostHistory (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                status_update_time DATETIME,
                status TEXT CHECK(status IN ('OK', 'NOT OK')),
                error_message TEXT,
                FOREIGN KEY (post_id) REFERENCES Posts(post_id)
            );
        """)
        

def create_comments_history_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                page_id INTEGER NOT NULL,
                ad_id TEXT NOT NULL,
                post_id TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,  -- 'sent' или 'scheduled'
                scheduled_time DATETIME,  -- Время, когда комментарий должен быть отправлен
                error_message TEXT,  -- Сообщение об ошибке, если что-то пошло не так
                FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
                FOREIGN KEY (page_id) REFERENCES FPages(page_id)
            );
        """)


def create_ai_content_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS AIContent (
                content_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                message_from_user TEXT,
                message_from_gpt TEXT,
                metadata JSON,
                FOREIGN KEY (post_id) REFERENCES Posts(post_id)
            );
        """)

def create_api_logs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS FBApiLogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_url TEXT NOT NULL,
                request_method TEXT NOT NULL,
                request_payload TEXT,
                response_status INTEGER,
                response_payload TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

def create_top_bayer_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS TOP (
                count INTEGER,
                login TEXT,
                FOREIGN KEY (login) REFERENCES users(login)
            );
        """)
        

def create_user_api_settings_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "user_api_settings" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER NOT NULL,
                "ai" TEXT NOT NULL,
                "ci" TEXT NOT NULL,
                "gi" TEXT NOT NULL,
                "x_trackbox_username" TEXT NOT NULL,
                "x_trackbox_password" TEXT NOT NULL,
                FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE
            );
        """)

def create_kt_api_logs_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS KTApiLogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_url TEXT NOT NULL,
                request_method TEXT NOT NULL,
                request_payload TEXT,
                response_status INTEGER,
                response_payload TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)




#Пиксели
def create_pixel_table_if_not_exists(conn):
    with conn:
        conn.execute("""
CREATE TABLE IF NOT EXISTS pixel (
    pixel INTEGER PRIMARY KEY,
    pixel_name TEXT NOT NULL
);

        """)


def create_pixel_users_table_if_not_exists(conn):
    with conn:
        conn.execute("""
CREATE TABLE IF NOT EXISTS pixel_users (
    pixel_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (pixel_id, user_id),
    FOREIGN KEY (pixel_id) REFERENCES pixels(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

        """)





#Лиды
def create_daily_leads_table_if_not_exists(conn):
    with conn:
        # Создаем таблицу, если ее нет
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subid TEXT,
                userip TEXT NOT NULL,
                firstname TEXT,
                lastname TEXT,
                email TEXT,
                phone TEXT,
                funnel TEXT,
                bayer TEXT,
                geo TEXT,
                lg TEXT,
                datatime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Получаем список существующих столбцов
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(leads_daily)")
        existing_columns = {row[1] for row in cursor.fetchall()}  # row[1] - название столбца

        # Определяем недостающие столбцы
        new_columns = {
            "kt_campaign_name": "TEXT",
            "kt_campaign_group": "TEXT",
            "kt_landing_group": "TEXT",
            "kt_offer_group": "TEXT",
            "kt_landing_name": "TEXT",
            "kt_offer_name": "TEXT",
            "kt_ffiliate_network": "TEXT",
            "kt_source_pixel": "TEXT",
            "kt_stream": "TEXT",
            "kt_global_source": "TEXT",
            "kt_referrer": "TEXT",
            "kt_keyword": "TEXT",
            "kt_click_id": "TEXT",
            "kt_visitor_code": "TEXT",
            "kt_campaign_id": "INTEGER",
            "kt_campaign_group_id": "INTEGER",
            "kt_offer_group_id": "INTEGER",
            "kt_landing_group_id": "INTEGER",
            "kt_landing_id": "INTEGER",
            "kt_offer_id": "INTEGER",
            "kt_affiliate_network": "TEXT",
            "kt_affiliate_network_id": "INTEGER",
            "kt_source_pixel_id": "INTEGER",
            "kt_stream_id": "INTEGER",
            "kt_fb_ad_campaign_name": "TEXT",
            "kt_external_id": "TEXT",
            "kt_creative_id": "TEXT",
            "kt_connection_type": "TEXT",
            "kt_operator": "TEXT",
            "kt_isp": "TEXT",
            "kt_country": "TEXT",
            "kt_region": "TEXT",
            "kt_city": "TEXT",
            "kt_language": "TEXT",
            "kt_device_type": "TEXT",
            "kt_user_agent": "TEXT",
            "kt_os": "TEXT",
            "kt_os_version": "TEXT",
            "kt_browser": "TEXT",
            "kt_browser_version": "TEXT",
            "kt_device_model": "TEXT",
            "kt_ip": "TEXT",
            "kt_postback_datetime": "TIMESTAMP",
            "kt_click_datetime": "TIMESTAMP",
            "kt_status": "TEXT",
            "kt_previous_status": "TEXT",
            "kt_original_status": "TEXT",
            "kt_conversion_id": "TEXT",
            "kt_cost": "REAL",
            "kt_sale_period": "INTEGER",
            "kt_profitability": "REAL",
            "kt_revenue": "REAL",
            
            "sale_status": "TEXT",
            "kt_profit": "REAL"
        }

                # Добавляем sub_id_1 ... sub_id_30
        for i in range(1, 31):
            new_columns[f"kt_sub_id_{i}"] = "TEXT"


        # Добавляем недостающие столбцы
        for column, data_type in new_columns.items():
            if column not in existing_columns:
                alter_query = f"ALTER TABLE leads_daily ADD COLUMN {column} {data_type};"
                conn.execute(alter_query)

        # 🔥 Добавляем индексы для быстрого поиска (создаются, если их нет)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_userip ON leads_daily(userip)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads_daily(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_subid ON leads_daily(subid)")


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


        


# РАсходы из кейтаро
def create_user_campaign_groups_table_if_not_exists(conn):
    with conn:
        conn.execute("""
CREATE TABLE IF NOT EXISTS "user_campaign_groups" (
    "user_id" INTEGER NOT NULL,
    "kt_campaign_group" TEXT NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
    PRIMARY KEY("user_id", "kt_campaign_group")
);


        """)

def insert_user_campaign_groups():
    # Подключение к базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Список данных для вставки
    data = [
        (28, 'Alex'),
        (25, 'Borz'),
        (18, 'Cart'),
        (24, 'Chak'),
        (9, 'David'),
        (10, 'Floyd'),
        (27, 'Rik'),
        (22, 'Sandra'),
        (8, 'Satoru1'),
        (21, 'Smal'),
        (7, 'ferz'),
        (16, 'mops')
    ]

    # SQL запрос для вставки данных
    query = '''
    INSERT OR IGNORE INTO user_campaign_groups (user_id, kt_campaign_group)
    VALUES (?, ?)
    '''

    # Выполнение запроса
    cursor.executemany(query, data)

    # Подтверждение изменений и закрытие соединения
    conn.commit()
    conn.close()



def create_domains_for_bot_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                country TEXT NOT NULL DEFAULT 'US'
            )
        """)

def create_cookies_for_bot_table_if_not_exists(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                cookies_str TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(domain)
            )
        """)




```text
cinema-pro-flask/
├── main.py                    # основной Flask-приложение, маршруты
├── db_requests/              # слой доступа к данным (SQL + MongoDB)
│   ├── main_requests.py      # запросы к MySQL (фильмы, актёры)
│   ├── count_requests.py     # подсчёт фильмов / актёров по фильтрам
│   └── save_find_mongo.py    # работа с MongoDB для аналитики
├── templates/ 
│   ├── base.html
│   ├── actors.html
|   ├── film_page.html
│   ├── films_by_actor.html
│   ├── genre.html
│   ├── home.html
│   ├── searching.html
│   ├── year.html
│   └── year_range.html
├── static/                   # CSS
├── local_settings.py         # настройки проекта, базы данных
├── .env.example              # пример конфигурации
├── requirements.txt          # зависимости Python
├── README.md / README.ru.md  # документация проекта


У вас также должны быть настройки подключения с вашими данными:

        dbconfig = {
    'host': HOST,
    'user': USER,
    'password': PASSWORD,
    'database': DATABASE,
    }
    
    HOST = ''
    USER = ''
    PASSWORD = ''
    DATABASE = ''

Основные моменты:

    Flask приложение:
    app = Flask(__name__, template_folder="templates")
    template_folder="templates" указывает, где искать HTML-шаблоны. 

    Основные обязанности app.py: 
        Обработка HTTP-запросов (@app.route)
        Вызов функций из слоя доступа к данным (db_requests)
        Передача данных в шаблоны (render_template)
        Пагинация (pagination() функция)
        Сохранение запросов в MongoDB (save_query())

Функция пагинации pagination(total_items, limit=10)

Объяснение:
    page — текущая страница, передаётся через GET параметр ?page=.
    limit — количество элементов на странице (например, 10 фильмов).
    offset — с какого элемента начинать выборку из базы данных.
    Возвращает словарь с параметрами для SQL-запроса и отображения навигации.
    Используется на всех страницах: фильмы, актёры, поиск.

| Маршрут                    | Назначение                | Используемые функции                                                 |
| -------------------------- | ------------------------- |----------------------------------------------------------------------|
| `/year/<int:year>`         | Фильмы конкретного года   | get_count_by_year(), get_films_by_year()                             |
| `/genre/<genre_name>`      | Фильмы конкретного жанра  | get_count_by_genre(), get_genre()                                    |
| `/searching`               | Поиск по ключевому слову  | get_count_by_search(), search_by_title()                             |
| `/year-range`              | Диапазон лет + жанр       | get_count_by_year_range(), get_films_by_year_range()                 |
| `/actors`                  | Список актёров            | get_total_actors(), get_actors()                                     |
| `/films_by/<int:actor_id>` | Фильмы конкретного актёра | get_films_count_by_actor(), get_films_by_actor(),  get_actor_by_id() |
|´/film/<int:film_id>´       | Для трейлеров фильма      | get_trailers()                                                       |



main_requests.py
Отвечает за получение всех фильмов, фильмов по фильтрам и актёров.

Примеры функций:

    def get_films(limit=10, offset=0):
        with mysql.connector.connect(**dbconfig_write) as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT
                        f.film_id,
                        f.title,
                        f.description,
                        f.release_year,
                        f.length,
                        f.rating,
                        f.image_url,
                        f.age_rating,
                        GROUP_CONCAT(g.name SEPARATOR ", ") AS genre -- Собираем ВСЕ жанры фильма в одну строку через запятую--
                        FROM films f
                JOIN film_genre fg ON fg.film_id = f.film_id
                JOIN genres g ON g.genre_id = fg.genre_id
                GROUP BY f.film_id -- Группируем строки по фильму чтобы GROUP_CONCAT корректно объединил жанры одного фильма
                ORDER BY f.rating DESC  
                LIMIT %s OFFSET %s;
    """
                cursor.execute(query, (limit, offset))
                return cursor.fetchall()
    
    
Объяснение: 

    GROUP_CONCAT собирает все жанры фильма в одну строку.
    ORDER BY f.rating DESC — сортировка по рейтингу.
    LIMIT + OFFSET — пагинация.
    Возвращает список словарей с данными фильма.


count_requests.py
Считает количество фильмов/актеров, чтобы работать с пагинацией.

Пример:

    def get_total_films():
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT COUNT(DISTINCT film_id) as total FROM films;"
            cursor.execute(query)
            return cursor.fetchone()["total"]

    
    
    Возвращает число уникальных фильмов.
    Используется в pagination().



save_find_mongo.py
Работа с MongoDB для аналитики:

    def save_query(query_type, key, result_count=None):
        queries_collection.update_one(
            {
                "query_type": query_type,
                "keyword": key
                },
        {
                "$inc": {"count": 1}, #Увеличивает значение поля count на 1
                "$set": {
                    "last_used": datetime.datetime.utcnow() #Устанавливает поле last_used равным текущему времени
                },
                "$setOnInsert": { #Эти поля будут установлены только при вставке нового документа
                    "created_at": datetime.datetime.utcnow(),
                    "result_count": result_count}
                },
                upsert=True)

Объяснение:

    query_type — тип запроса (year, genre, search_by_keyword, films_by_actor)
    key — ключ запроса (год, жанр, слово или актёр)
    $inc — увеличивает счетчик, если запрос уже есть
    $set — обновляет время последнего запроса
    $setOnInsert — создаёт новые поля при вставке нового запроса
    upsert=True — создаёт запись, если её нет


Также есть:

def get_popular_queries():
    return list(queries_collection.find().sort("count", -1).limit(5)) #Показывает топ-5 популярных

def get_recent_queries():
    return list(queries_collection.find().sort("last_used", -1).limit(5)) #Показывает 5 последних поисков



Поток работы проекта (end-to-end): 

    Пользователь открывает страницу / или фильтрует по жанру / году.
    Flask маршрут вызывает функции слоя доступа к данным (MySQL + MongoDB)
    Считается количество элементов → пагинация
    Извлекаются данные для текущей страницы → фильмы, актеры, жанры
    Сохраняется аналитика поисковых действий в MongoDB
    Передаём всё в шаблон → HTML рендерится и отображается

    Пользователь видит страницу с:

        фильмами
        жанрами
        популярными и последними запросами
        навигацией по страницам

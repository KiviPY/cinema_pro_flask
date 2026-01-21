cinema-pro-flask/
├── main.py # Main Flask application with routes
├── db_requests/ # Data access layer (SQL + MongoDB)
│ ├── main_requests.py # MySQL queries (movies, actors)
│ ├── count_requests.py # Counting movies/actors by filters
│ └── save_find_mongo.py # MongoDB analytics
├── templates/
│ ├── base.html
│ ├── actors.html
│ ├── films_by_actor.html
│ ├── genre.html
│ ├── home.html
│ ├── searching.html
│ ├── year.html
│ └── year_range.html
├── static/ # CSS files
├── local_settings.py # Project & database settings
├── .env.example # Example configuration
├── requirements.txt # Python dependencies
├── README.md / README.ru.md # Project documentation


You should also have connection settings with your data:

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


app = Flask(__name__, template_folder="templates")
template_folder="templates" specifies where to find HTML templates.

Responsibilities of main.py:

    Handle HTTP requests (@app.route)
    Call functions from the data access layer (db_requests)
    Pass data to templates (render_template)
    Pagination (pagination() function)
    Save user queries in MongoDB (save_query())


Example: 

def pagination(total_items, limit=10):
    page = request.args.get("page", 1, type=int)
    total_pages = (total_items + limit - 1) // limit
    offset = (page - 1) * limit
    return {"page": page, "limit": limit, "offset": offset, "total_pages": total_pages}

Description: 

    page — current page, passed via GET parameter ?page=
    limit — number of items per page (e.g., 10 movies)
    offset — starting point for SQL query
    Returns dictionary with pagination parameters
    Used on all pages: movies, actors, search


| Route                      | Purpose                    | Functions Used                                                      |
| -------------------------- | -------------------------- | ------------------------------------------------------------------- |
| `/year/<int:year>`         | Movies of a specific year  | get_count_by_year(), get_films_by_year()                            |
| `/genre/<genre_name>`      | Movies of a specific genre | get_count_by_genre(), get_genre()                                   |
| `/searching`               | Search by keyword          | get_count_by_search(), search_by_title()                            |
| `/year-range`              | Year range + genre         | get_count_by_year_range(), get_films_by_year_range()                |
| `/actors`                  | List of actors             | get_total_actors(), get_actors()                                    |
| `/films_by/<int:actor_id>` | Movies by a specific actor | get_films_count_by_actor(), get_films_by_actor(), get_actor_by_id() |



main_requests.py

Handles retrieving movies, filtered movies, and actors.

Example:

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
                        GROUP_CONCAT(g.name SEPARATOR ", ") AS genre
                    FROM films f
                    JOIN film_genre fg ON fg.film_id = f.film_id
                    JOIN genres g ON g.genre_id = fg.genre_id
                    GROUP BY f.film_id
                    ORDER BY f.rating DESC
                    LIMIT %s OFFSET %s;
                """
                cursor.execute(query, (limit, offset))
                return cursor.fetchall()


Explanation:

    GROUP_CONCAT combines all genres of a movie into one string.
    ORDER BY f.rating DESC sorts by rating.
    LIMIT + OFFSET handles pagination.
    Returns a list of dictionaries with movie data.


count_requests.py
Counts movies/actors for pagination.

Example:

    def get_total_films():
        with mysql.connector.connect(**dbconfig_write) as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT COUNT(DISTINCT film_id) as total FROM films;"
                cursor.execute(query)
                return cursor.fetchone()["total"]


Returns the total number of unique movies
Used in pagination()


save_find_mongo.py
Handles MongoDB analytics:
    
    def save_query(query_type, key, result_count=None):
        queries_collection.update_one(
            {
                "query_type": query_type,
                "keyword": key
            },
            {
                "$inc": {"count": 1},               # Increase count if exists
                "$set": {"last_used": datetime.datetime.utcnow()}, # Update last used
                "$setOnInsert": {                   # Only on insert
                    "created_at": datetime.datetime.utcnow(),
                    "result_count": result_count
                }
            },
            upsert=True
        )

Description: 

    query_type — type of query (year, genre, search_by_keyword, films_by_actor)
    key — query key (year, genre, keyword, actor)
    $inc — increments count if document exists
    $set — updates last_used timestamp
    $setOnInsert — sets fields on insert only
    upsert=True — creates document if it does not exist



Other useful functions:
    
    def get_popular_queries():
        return list(queries_collection.find().sort("count", -1).limit(5))
    
    def get_recent_queries():
        return list(queries_collection.find().sort("last_used", -1).limit(5))

Returns top-5 popular queries and 5 most recent queries



Project Workflow (End-to-End)

    User opens / or filters by genre/year
    Flask route calls functions from the data access layer (MySQL + MongoDB)
    Count total items → pagination
    Fetch data for current page → movies, actors, genres
    Save search analytics in MongoDB
    Pass data to template → HTML is rendered and displayed
    User sees page with:

        Movies
        Genres
        Popular and recent queries
        Page navigation
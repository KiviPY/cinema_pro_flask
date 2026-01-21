from local_settings import dbconfig_write
import mysql.connector
dbconfig_write['database'] = 'movies'


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


def get_genre(genre, limit=10, offset=0):
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
                WHERE g.name = %s
                GROUP BY f.film_id
                LIMIT %s OFFSET %s;
"""
            cursor.execute(query, (genre, limit, offset))
            return cursor.fetchall()



def search_by_title(keyword, limit=10, offset=0):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
                query_prefix = """
                    SELECT
                        f.film_id,
                        f.title,
                        f.description,
                        f.release_year,
                        f.rating,
                        f.length,
                        f.age_rating,
                        f.image_url,
                        GROUP_CONCAT(g.name SEPARATOR ", ") AS genre
                    FROM films f
                    JOIN film_genre fg ON fg.film_id = f.film_id
			        JOIN genres g ON g.genre_id = fg.genre_id
                    WHERE title LIKE CONCAT(%s, '%%')
                    GROUP BY f.film_id
                    LIMIT %s OFFSET %s;
"""
                cursor.execute(query_prefix, (keyword, limit, offset))
                return cursor.fetchall()


def get_films_by_year(year, limit=10, offset=0):
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
                WHERE f.release_year = %s
                GROUP BY f.film_id
                LIMIT %s OFFSET %s;
"""
            cursor.execute(query, (year, limit, offset))
            return cursor.fetchall()


def get_films_by_year_range(start_year, end_year, genre, limit=10, offset=0):
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
                WHERE f.release_year BETWEEN %s AND %s
                AND (%s IS NULL OR g.name = %s)
                GROUP BY f.film_id
                LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (start_year, end_year, genre, genre, limit, offset))
            return cursor.fetchall()



def get_actors(limit=10, offset=0):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT actor_id, first_name, last_name, photo_url
                FROM actors
                LIMIT %s OFFSET %s;
"""
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()


def get_films_by_actor(actor_id, limit=10, offset=0):
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
                JOIN film_actor f_a ON f.film_id = f_a.film_id
                JOIN actors a ON f_a.actor_id = a.actor_id
                WHERE a.actor_id = %s
                GROUP BY f.film_id
                LIMIT %s OFFSET %s;
"""
            cursor.execute(query, (actor_id, limit, offset))
            return cursor.fetchall()

def get_actor_by_id(actor_id):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT first_name, last_name FROM actors WHERE actor_id = %s;
"""
            cursor.execute(query, (actor_id,))
            return cursor.fetchone()


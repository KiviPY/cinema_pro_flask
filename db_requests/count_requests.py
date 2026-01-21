from local_settings import dbconfig_write
import mysql.connector
dbconfig_write['database'] = 'movies'



def get_total_films():
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT COUNT(DISTINCT film_id) as total FROM films;"
            cursor.execute(query)
            return cursor.fetchone()["total"]


def get_count_by_genre(genre):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                    SELECT COUNT(DISTINCT f.film_id) as total
                    FROM films f
                    JOIN film_genre fg ON fg.film_id = f.film_id
			        JOIN genres g ON g.genre_id = fg.genre_id
                    WHERE g.name = %s;
"""
            cursor.execute(query, (genre,))
            return cursor.fetchone()['total']


def get_count_by_year(year):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT COUNT(DISTINCT film_id) AS total FROM films
                WHERE release_year = %s;
"""
            cursor.execute(query, (year,))
            return cursor.fetchone()['total']


def get_count_by_search(keyword):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT COUNT(DISTINCT film_id) AS total
                FROM films
                WHERE title LIKE CONCAT(%s, '%%');
"""
            cursor.execute(query, (keyword,))
            return cursor.fetchone()["total"]

def get_count_by_year_range(start_year, end_year, genre):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query ="""
                SELECT COUNT(DISTINCT f.film_id) AS total FROM films f
                JOIN film_genre fg ON fg.film_id = f.film_id
			    JOIN genres g ON g.genre_id = fg.genre_id
                WHERE f.release_year BETWEEN %s AND %s
                AND (%s IS NULL OR g.name = %s);
"""
            cursor.execute(query, (start_year, end_year, genre, genre)) # если genre == NULL = условие TRUE жанр НЕ фильтруется
            return cursor.fetchone()["total"]                                   # если genre НЕ NULL = выбираем только фильмы с этим жанром




def get_year_bounds():
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT
                    MIN(release_year) AS min_year,
                    MAX(release_year) AS max_year
                FROM films;
"""
            cursor.execute(query)
            return cursor.fetchone()


def get_total_actors():
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT COUNT(DISTINCT actor_id) AS total FROM actors;
"""
            cursor.execute(query)
            return cursor.fetchone()['total']

def get_films_count_by_actor(actor_id):
    with mysql.connector.connect(**dbconfig_write) as conn:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                    SELECT COUNT(DISTINCT f.film_id) AS total FROM films f
                    JOIN film_actor f_a ON f.film_id = f_a.film_id
                    JOIN actors a ON f_a.actor_id = a.actor_id
                    WHERE a.actor_id = %s;
"""
            cursor.execute(query, (actor_id,))
            return cursor.fetchone()['total']

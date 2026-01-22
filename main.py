from flask import Flask, render_template, request
from db_requests.main_requests import *
from db_requests.count_requests import *
from db_requests.save_find_mongo import *
app = Flask(__name__, template_folder="templates")


def pagination(total_items, limit=10): # функция для пагинации
    page = request.args.get("page", 1, type=int) # деф значение
    total_pages = (total_items + limit - 1) // limit
    offset = (page - 1) * limit
    return {"page": page, "limit": limit, "offset": offset, "total_pages": total_pages}


@app.route("/")
@app.route("/home")
def home():
    total_films = get_total_films()
    pager = pagination(total_films, limit=10)
    films = get_films(limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()

    return render_template("home.html", films=films, popular_queries=popular_queries, recent_queries=recent_queries, **pager)


@app.route("/year/<int:year>")
def year_page(year):
    total_films = get_count_by_year(year)
    pager = pagination(total_films, limit=10)
    films = get_films_by_year(year, limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    save_query(query_type="year", key=str(year), page=pager["page"], result_count=total_films)

    return render_template("year.html", films=films, year=year, popular_queries=popular_queries, recent_queries=recent_queries, **pager)


@app.route("/genre/<genre_name>")
def genre_page(genre_name):
    total_films = get_count_by_genre(genre_name)
    pager = pagination(total_films, limit=10)
    films = get_genre(genre_name, limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    save_query(query_type="genre", key=genre_name, page=pager["page"], result_count=total_films)

    return render_template("genre.html", films=films, genre=genre_name, popular_queries=popular_queries, recent_queries=recent_queries, **pager)

@app.route("/searching")
def searching():
    keyword = request.args.get("word")
    total_films = get_count_by_search(keyword)
    pager = pagination(total_films, limit=10)
    films = search_by_title(keyword, limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    save_query(query_type="search_by_keyword", key=keyword, page=pager["page"], result_count=total_films)

    return render_template("searching.html", films=films, keyword=keyword, popular_queries=popular_queries, recent_queries=recent_queries, **pager)


@app.route("/year-range")
def year_range():
    bounds = get_year_bounds()
    min_year = bounds["min_year"]
    max_year = bounds["max_year"]

    start_year = request.args.get("start", type=int) or min_year
    end_year = request.args.get("end", type=int) or max_year
    genre = request.args.get("genre")

    total_films = get_count_by_year_range(start_year, end_year, genre)
    pager = pagination(total_films, limit=10)
    films = get_films_by_year_range(start_year, end_year, genre, limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    save_query(query_type="year_range", key=f"{start_year}-{end_year}-{genre}", page=pager["page"], result_count=total_films)

    return render_template("year_range.html",films=films, start_year=start_year, end_year=end_year, genre=genre, popular_queries=popular_queries, recent_queries=recent_queries, **pager)



@app.route("/actors")
def actors_page():
    total_actors = get_total_actors()
    pager = pagination(total_actors, limit=24)
    actors = get_actors(limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()

    return render_template("actors.html", actors=actors,  popular_queries=popular_queries, recent_queries=recent_queries, **pager)

@app.route("/films_by/<int:actor_id>")
def films_by_actor(actor_id):
    total_films = get_films_count_by_actor(actor_id)
    pager = pagination(total_films, limit=10)
    films = get_films_by_actor(actor_id, limit=pager["limit"], offset=pager["offset"])

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    actor_info = get_actor_by_id(actor_id)
    save_query(query_type="films_by_actor", key={"actor_id": actor_id, "first_name": actor_info["first_name"], "last_name": actor_info["last_name"]}, page=pager["page"], result_count=total_films)

    return render_template("films_by_actor.html", films=films, actor_id=actor_id,  popular_queries=popular_queries, recent_queries=recent_queries, **pager)


@app.route("/film/<int:film_id>")
def film_page(film_id):
    film = get_trailer(film_id)  # получаем данные фильма вместе с трейлером
    if not film:
        return "Film not found", 404

    popular_queries = get_popular_queries()
    recent_queries = get_recent_queries()
    save_query(query_type="film", key=film["title"], page=1, result_count=1)

    return render_template("film_page.html", film=film, popular_queries=popular_queries, recent_queries=recent_queries, page=1, total_pages=1)


if __name__ == "__main__":
    app.run(debug=True)

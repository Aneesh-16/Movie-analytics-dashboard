"""Example client for the partner's Recommendation app. It only needs the shared API base URL.
    from partner_client import SharedMovieAPI
    api = SharedMovieAPI("https://YOUR-SERVICE.onrender.com")   # the same API_BASE_URL I use
    api.login("partner_user", "their-password")                  # or api.register(...) first
    movie = api.movie(155); api.rate(155, 9); api.watchlist_add(155)
Recommendation logic stays in the partner's project; this client only reads movies and stores events."""
import httpx


class SharedMovieAPI:
    def __init__(self, base_url: str, http: httpx.Client | None = None):
        self.http = http or httpx.Client(base_url=base_url, timeout=20)   # tests inject a FastAPI TestClient
        self.headers: dict = {}

    def _call(self, method, path, **kw):
        r = self.http.request(method, path, headers=self.headers, **kw)
        r.raise_for_status()
        return r.json()

    # ---- account ----
    def register(self, username, password):
        return self._call("POST", "/api/users/register", json={"username": username, "password": password})

    def login(self, username, password):
        data = self._call("POST", "/api/auth/login", json={"username": username, "password": password})
        self.headers = {"Authorization": "Bearer " + data["token"]}
        self.username = data["username"]
        return data

    # ---- movie data (the same TMDB ids as the analytics dashboard) ----
    def movies(self, **filters):               # q, genre, language, year_from, year_to, min_rating, min_votes, sort, offset, limit
        return self._call("GET", "/api/movies", params=filters)

    def movie(self, movie_id):
        return self._call("GET", f"/api/movies/{movie_id}")

    def patch_movie(self, movie_id, **fields):  # editor accounts only
        return self._call("PATCH", f"/api/movies/{movie_id}", json=fields)

    # ---- interactions ----
    def interact(self, movie_id, interaction_type, rating=None, metadata=None):
        return self._call("POST", "/api/interactions", json={"movie_id": movie_id, "interaction_type": interaction_type,
                                                              "rating": rating, "metadata": metadata})

    def rate(self, movie_id, rating):
        return self.interact(movie_id, "rating", rating=rating)

    def like(self, movie_id):
        return self.interact(movie_id, "like")

    def watchlist_add(self, movie_id):
        return self.interact(movie_id, "watchlist_add")

    def watchlist_remove(self, movie_id):
        return self.interact(movie_id, "watchlist_remove")

    def recommendation_shown(self, movie_id, source_movie_id=None, algorithm=None):
        return self.interact(movie_id, "recommendation_impression", metadata={"source_movie_id": source_movie_id, "algorithm": algorithm})

    def recommendation_clicked(self, movie_id, source_movie_id=None, algorithm=None):
        return self.interact(movie_id, "recommendation_click", metadata={"source_movie_id": source_movie_id, "algorithm": algorithm})

    def recommendation_feedback(self, movie_id, relevant: bool, **extra):   # source_movie_id, algorithm, comment
        return self._call("POST", "/api/recommendation-feedback",
                          json={"movie_id": movie_id, "feedback": "relevant" if relevant else "not_relevant", **extra})

    def my_watchlist(self):
        return self._call("GET", f"/api/users/{self.username}/watchlist")

    def my_ratings(self):
        return self._call("GET", f"/api/users/{self.username}/ratings")

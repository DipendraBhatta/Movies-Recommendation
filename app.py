# movie_recommender_app.py

import os
import pickle
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY is not set.")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# --------------------------
# TMDB Poster Fetch Function
# --------------------------
def fetch_poster_by_title(title: str) -> str:
    """Fetch movie poster from TMDB API using the movie title."""
    try:
        params = {"api_key": TMDB_API_KEY, "query": title}
        resp = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results") or []
        if results:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return f"{TMDB_IMAGE_BASE}/{poster_path}"
    except requests.RequestException as e:
        # Log to Streamlit sidebar for visibility during dev
        st.sidebar.warning(f"TMDB request failed: {e}")

    # Fallback placeholder
    return "https://via.placeholder.com/500x750?text=Poster+Not+Found"

# --------------------------
# Movie Recommendation Function
# --------------------------
def recommend(movie: str):
    """Return top 5 recommended movie titles and their posters."""
    try:
        index = movies[movies["title"] == movie].index[0]
    except IndexError:
        st.error("Movie not found in database!")
        return [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names, posters = [], []
    for i in distances[1:6]:  # top 5 recommendations
        title = movies.iloc[i[0]]["title"]
        names.append(title)
        posters.append(fetch_poster_by_title(title))
    return names, posters

# --------------------------
# Streamlit App Configuration
# --------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header("🎬 Movie Recommender System")

# Load movies and similarity matrix
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# Movie selection dropdown
movie_list = movies["title"].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# Show recommendations
if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])

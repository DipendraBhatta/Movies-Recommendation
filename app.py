# app.py
import os
import pickle
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# --------------------------
# TMDB API setup
# --------------------------
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY is not set.")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# --------------------------
# Poster fetch function
# --------------------------
def fetch_poster_by_title(title: str) -> str:
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
        st.sidebar.warning(f"TMDB request failed: {e}")
    return "https://via.placeholder.com/500x750?text=Poster+Not+Found"

# --------------------------
# Recommendation function
# --------------------------
def recommend(movie: str):
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
# Streamlit app config
# --------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header("🎬 Movie Recommender System")

# --------------------------
# Paths for pickle files
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_dict_path = os.path.join(BASE_DIR, "movie_dict.pkl")
similarity_path = os.path.join(BASE_DIR, "similarity.pkl")

# --------------------------
# Google Drive URLs for pickles
# --------------------------
MOVIE_DICT_URL = "https://drive.google.com/uc?export=download&id=1ZEaU9wCjRPRMV11BYqJ41ibF6CUUtfDE"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1D-Dktq_PzfIFs1kEvQQNQV2hae8jCchK"

# --------------------------
# Download pickles if missing
# --------------------------
def download_file(url, path):
    if not os.path.exists(path):
        st.info(f"Downloading {os.path.basename(path)} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        st.success(f"{os.path.basename(path)} downloaded!")

download_file(MOVIE_DICT_URL, movies_dict_path)
download_file(SIMILARITY_URL, similarity_path)

# --------------------------
# Load pickles
# --------------------------
with open(movies_dict_path, "rb") as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open(similarity_path, "rb") as f:
    similarity = pickle.load(f)

# --------------------------
# Movie selection dropdown
# --------------------------
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

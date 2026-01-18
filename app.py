# app.py

import os
import pickle
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY is not set.")

# --------------------------
# TMDB API Constants
# --------------------------
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# --------------------------
# Google Drive URLs for pickles
# --------------------------
MOVIE_DICT_URL = "https://drive.google.com/uc?export=download&id=1ZEaU9wCjRPRMV11BYqJ41ibF6CUUtfDE"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1D-Dktq_PzfIFs1kEvQQNQV2hae8jCchK"

# --------------------------
# Paths for local pickles
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIE_DICT_PATH = os.path.join(BASE_DIR, "movie_dict.pkl")
SIMILARITY_PATH = os.path.join(BASE_DIR, "similarity.pkl")

# --------------------------
# Function to download pickles if missing
# --------------------------
def download_file(url, path):
    if not os.path.exists(path):
        st.info(f"Downloading {os.path.basename(path)} ...")
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            st.success(f"{os.path.basename(path)} downloaded!")
        except requests.RequestException as e:
            st.error(f"Failed to download {os.path.basename(path)}: {e}")
            st.stop()

# --------------------------
# Download pickles if needed
# --------------------------
download_file(MOVIE_DICT_URL, MOVIE_DICT_PATH)
download_file(SIMILARITY_URL, SIMILARITY_PATH)

# --------------------------
# Load movies and similarity
# --------------------------
with open(MOVIE_DICT_PATH, "rb") as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open(SIMILARITY_PATH, "rb") as f:
    similarity = pickle.load(f)

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header("🎬 Movie Recommender System")

# --------------------------
# Function to fetch movie poster from TMDB
# --------------------------
def fetch_poster_by_title(title: str) -> str:
    try:
        params = {"api_key": TMDB_API_KEY, "query": title}
        resp = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if results and results[0].get("poster_path"):
            return f"{TMDB_IMAGE_BASE}/{results[0]['poster_path']}"
    except requests.RequestException as e:
        st.sidebar.warning(f"TMDB request failed: {e}")
    # Fallback placeholder
    return "https://via.placeholder.com/500x750?text=Poster+Not+Found"

# --------------------------
# Movie Recommendation Function
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
# Movie Selection Dropdown
# --------------------------
movie_list = movies["title"].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# --------------------------
# Show Recommendations
# --------------------------
if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])

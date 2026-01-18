# app.py
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
    for i in distances[1:6]:
        title = movies.iloc[i[0]]["title"]
        names.append(title)
        posters.append(fetch_poster_by_title(title))
    return names, posters

# --------------------------
# Streamlit App Config
# --------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header("🎬 Movie Recommender System")

# --------------------------
# File paths
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_dict_path = os.path.join(BASE_DIR, "movie_dict.pkl")
similarity_path = os.path.join(BASE_DIR, "similarity.pkl")

# --------------------------
# Google Drive file IDs
# --------------------------
MOVIE_DICT_ID = "1ZEaU9wCjRPRMV11BYqJ41ibF6CUUtfDE"
SIMILARITY_ID = "1D-Dktq_PzfIFs1kEvQQNQV2hae8jCchK"

# --------------------------
# Function to download Google Drive files
# --------------------------
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)

    # Google shows a confirm token for large files
    def get_confirm_token(resp):
        for k, v in resp.cookies.items():
            if k.startswith("download_warning"):
                return v
        return None

    token = get_confirm_token(response)
    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# --------------------------
# Download files if missing
# --------------------------
if not os.path.exists(movies_dict_path):
    st.info("Downloading movie_dict.pkl ...")
    download_file_from_google_drive(MOVIE_DICT_ID, movies_dict_path)
    st.success("movie_dict.pkl downloaded!")

if not os.path.exists(similarity_path):
    st.info("Downloading similarity.pkl ...")
    download_file_from_google_drive(SIMILARITY_ID, similarity_path)
    st.success("similarity.pkl downloaded!")

# --------------------------
# Load pickles
# --------------------------
with open(movies_dict_path, "rb") as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open(similarity_path, "rb") as f:
    similarity = pickle.load(f)

# --------------------------
# Movie dropdown and recommendations
# --------------------------
movie_list = movies["title"].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])

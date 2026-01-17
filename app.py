# movie_recommender_app.py

import streamlit as st
import pickle
import pandas as pd
import requests

# --------------------------
# TMDB Poster Fetch Function
# --------------------------
def fetch_poster_by_title(title):
    """Fetch movie poster from TMDB API using the movie title."""
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    
    response = requests.get(url).json()
    
    if response.get('results'):
        poster_path = response['results'][0].get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
    
    # Return placeholder if poster not found
    return "https://via.placeholder.com/500x750?text=Poster+Not+Found"

# --------------------------
# Movie Recommendation Function
# --------------------------
def recommend(movie):
    """Return top 5 recommended movie titles and their posters."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in database!")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in distances[1:6]:  # top 5 recommendations
        title = movies.iloc[i[0]]['title']
        recommended_movie_names.append(title)
        recommended_movie_posters.append(fetch_poster_by_title(title))
    
    return recommended_movie_names, recommended_movie_posters

# --------------------------
# Streamlit App Configuration
# --------------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.header("🎬 Movie Recommender System")

# Load movies and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Movie selection dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# Show recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[idx])
                st.image(recommended_movie_posters[idx])

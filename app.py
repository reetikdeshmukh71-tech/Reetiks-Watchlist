
import streamlit as st
import pandas as pd
import ast
import requests

TMDB_API_KEY = "33aa6d78054fc5613263f3e0bba790ce"

st.set_page_config(
    page_title="Reetik's Watchlist 🍿",
    layout="wide"
)

st.title("🎬 Reetik's Watchlist 🍿")
st.write("Movie Recommendation System")

movies = pd.read_csv(
    "/content/drive/MyDrive/Reetiks_Watchlist/tmdb_5000_movies.csv"
)

credits = pd.read_csv(
    "/content/drive/MyDrive/Reetiks_Watchlist/tmdb_5000_credits.csv"
)

movies["genres"] = movies["genres"].apply(
    lambda x: [i["name"] for i in ast.literal_eval(x)]
)

credits["cast"] = credits["cast"].apply(
    lambda x: [i["name"] for i in ast.literal_eval(x)][:5]
)

data = movies[
    ["id", "title", "genres", "vote_average", "overview"]
].copy()

data["cast"] = credits["cast"]


@st.cache_data
def get_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    try:
        response = requests.get(
            url,
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            poster_path = response.json().get("poster_path")

            if poster_path:
                return (
                    "https://image.tmdb.org/t/p/w500"
                    + poster_path
                )

    except requests.RequestException:
        pass

    return None


def recommend(movie):
    selected = data[data["title"] == movie].iloc[0]

    scores = data.apply(
        lambda x:
        len(set(selected["genres"]) & set(x["genres"])) +
        len(set(selected["cast"]) & set(x["cast"])),
        axis=1
    )

    scores.loc[selected.name] = -1

    return data.loc[scores.nlargest(6).index]


movie = st.selectbox(
    "🔎 Select a movie",
    data["title"].tolist()
)

if st.button("🎯 Recommend Movies"):

    selected = data[data["title"] == movie].iloc[0]

    st.subheader(f"🎬 {selected['title']}")

    col1, col2 = st.columns([1, 2])

    with col1:
        image = get_poster(selected["id"])

        if image:
            st.image(image, width=250)
        else:
            st.info("Poster unavailable")

    with col2:
        st.write("⭐ Rating:", selected["vote_average"])
        st.write("🎭 Genres:", ", ".join(selected["genres"]))
        st.write("👥 Cast:", ", ".join(selected["cast"]))
        st.write("📝", selected["overview"])

    st.divider()
    st.subheader("🤖 Recommended Movies")

    results = recommend(movie)

    cols = st.columns(3)

    for i, (_, m) in enumerate(results.iterrows()):

        with cols[i % 3]:
            image = get_poster(m["id"])

            if image:
                st.image(image, width=180)
            else:
                st.write("🎬 Poster unavailable")

            st.write(f"**{m['title']}**")
            st.write(f"⭐ {m['vote_average']}")

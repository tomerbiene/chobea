import streamlit as st
import requests
import random
import urllib.parse

# TMDB API Key
API_KEY = "9da4331eb5011edb49d11a04767898a2"
BASE_URL = "https://api.themoviedb.org/3"

# Page Configuration
st.set_page_config(page_title="Chobea | Cinema Curator", page_icon="🐝", layout="wide", initial_sidebar_state="expanded")

# --- CSS: CLEAN THEME & FIXED IMAGE SIZES ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    /* Grid içindeki afişlerin milimetrik aynı boyda kalmasını sağlar */
    div[data-testid="stImage"] img {
        height: 380px !important;
        object-fit: cover !important;
        border-radius: 8px !important;
    }
    .disclaimer-text {
        color: #888888;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .legal-text {
        color: #aaaaaa;
        font-size: 0.75rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- MEMORY & STATE MANAGEMENT ---
if "shown_movies" not in st.session_state: st.session_state.shown_movies = []
if "current_results" not in st.session_state: st.session_state.current_results = []
if "current_type" not in st.session_state: st.session_state.current_type = "movie"
if "daily_hive" not in st.session_state: st.session_state.daily_hive = []

if "selected_director_id" not in st.session_state: st.session_state.selected_director_id = None
if "selected_director_name" not in st.session_state: st.session_state.selected_director_name = None
if "dir_selected_movie" not in st.session_state: st.session_state.dir_selected_movie = None

if "selected_actor_id" not in st.session_state: st.session_state.selected_actor_id = None
if "selected_actor_name" not in st.session_state: st.session_state.selected_actor_name = None
if "act_selected_movie" not in st.session_state: st.session_state.act_selected_movie = None


# --- STATE FUNCTIONS ---
def set_director(id, name):
    st.session_state.selected_director_id = id
    st.session_state.selected_director_name = name
    st.session_state.dir_selected_movie = None


def reset_director():
    st.session_state.selected_director_id = None
    st.session_state.selected_director_name = None
    st.session_state.dir_selected_movie = None


def set_actor(id, name):
    st.session_state.selected_actor_id = id
    st.session_state.selected_actor_name = name
    st.session_state.act_selected_movie = None


def reset_actor():
    st.session_state.selected_actor_id = None
    st.session_state.selected_actor_name = None
    st.session_state.act_selected_movie = None


def view_dir_movie(movie): st.session_state.dir_selected_movie = movie


def back_to_dir_list(): st.session_state.dir_selected_movie = None


def view_act_movie(movie): st.session_state.act_selected_movie = movie


def back_to_act_list(): st.session_state.act_selected_movie = None


@st.cache_data(show_spinner=False)
def get_showcase(category="director"):
    if category == "director":
        names = ["Christopher Nolan", "Quentin Tarantino", "David Fincher", "Martin Scorsese", "Denis Villeneuve",
                 "Stanley Kubrick"]
    else:
        names = ["Leonardo DiCaprio", "Christian Bale", "Brad Pitt", "Cillian Murphy", "Robert De Niro", "Al Pacino"]

    showcase_list = []
    for name in names:
        res = requests.get(f"{BASE_URL}/search/person", params={"api_key": API_KEY, "query": name, "language": "en-US"})
        if res.status_code == 200 and res.json().get("results"):
            person = res.json()["results"][0]
            showcase_list.append({"name": person["name"], "id": person["id"], "photo": person.get("profile_path")})
    return showcase_list


# --- REUSABLE DETAIL VIEW COMPONENT ---
def render_movie_detail(movie, back_function):
    st.button("🔙 Back to Filmography", on_click=back_function)
    st.write("")

    col1, col2 = st.columns([1, 2])
    title = movie.get("title", movie.get("name", "Unknown"))

    with col1:
        if movie.get("poster_path"):
            st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", use_container_width=True)
        search_query = urllib.parse.quote(f"{title} official trailer")
        st.link_button("🎬 Watch Trailer (YouTube)", f"https://www.youtube.com/results?search_query={search_query}",
                       use_container_width=True)

    with col2:
        st.markdown(f"<h1 style='margin-bottom:0;'>{title}</h1>", unsafe_allow_html=True)
        date = movie.get('release_date', 'Unknown')
        score = movie.get('vote_average', 0)
        st.markdown(f"<h4 style='color:gray; font-weight:normal;'>🗓️ {date[:4]} | ⭐ {score:.1f} / 10</h4>",
                    unsafe_allow_html=True)
        st.divider()
        st.write(movie.get("overview", "No overview available for this title."))


# --- SIDEBAR (FILTERS ONLY) ---
with st.sidebar:
    st.header("🍯 Filter Your Hive")
    st.caption("Adjust your preferences below.")

    c_type = st.radio("1. What are you looking for?", ["🎬 Movie", "📺 TV Show & Mini-Series", "🎨 Anime & Animation"])
    c_pool = st.radio("2. What caliber do you prefer?", ["🏆 Cult Classics", "💎 Hidden Gems", "🍿 Popular Hits"])
    c_time = st.radio("3. What's your time budget?",
                      ["⏱️ Quick (Under 100 min)", "⏱️ Standard (100 - 130 min)", "⏱️ Marathon (130+ min)"])

# --- HERO SECTION ---
st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>🐝 Chobea</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 1.2rem; font-style: italic; margin-bottom: 0.5rem;'>Curating 3 masterpieces into your hive from thousands of films.</p>",
    unsafe_allow_html=True)
st.markdown(
    "<p class='disclaimer-text'>*Disclaimer: Chobea is a legal cinema curation assistant. We do not host or stream copyrighted content. Grab your popcorn and watch on your favorite official platforms!*</p>",
    unsafe_allow_html=True)
st.markdown("<p class='legal-text'>This product uses the TMDB API but is not endorsed or certified by TMDB.</p>",
            unsafe_allow_html=True)

tab_main, tab_director, tab_actor = st.tabs(["🎲 Smart Choice", "🎥 Director Archive", "🎭 Actor Archive"])

# ==========================================
# 1. TAB: SMART CHOICE (MAIN DASHBOARD)
# ==========================================
with tab_main:
    st.write("")
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        extract_button = st.button("🐝 EXTRACT 3 MASTERPIECES", type="primary", use_container_width=True)

    st.divider()

    if extract_button:
        with st.spinner("Extracting masterpieces from the archive..."):
            endpoint = "movie" if c_type != "📺 TV Show & Mini-Series" else "tv"
            params = {"api_key": API_KEY, "language": "en-US", "page": 1}

            if c_type == "🎬 Movie":
                params["without_genres"] = "16"
            elif c_type == "🎨 Anime & Animation":
                params["with_genres"] = "16"

            if c_pool == "🏆 Cult Classics":
                params["sort_by"] = "vote_count.desc"
                params["vote_average.gte"] = 8.0
                if c_type == "🎬 Movie":
                    params["vote_count.gte"] = 10000
                elif c_type == "📺 TV Show & Mini-Series":
                    params["vote_count.gte"] = 3000
                else:
                    params["vote_count.gte"] = 1500
            elif c_pool == "💎 Hidden Gems":
                params["sort_by"] = "vote_average.desc"
                params["vote_average.gte"] = 7.4
                if c_type == "🎬 Movie":
                    params["vote_count.gte"] = 300
                    params["vote_count.lte"] = 3000
                else:
                    params["vote_count.gte"] = 100
                    params["vote_count.lte"] = 1500
            else:
                params["sort_by"] = "popularity.desc"
                if c_type == "🎬 Movie":
                    params["vote_count.gte"] = 1500
                else:
                    params["vote_count.gte"] = 500

            if endpoint == "movie":
                if c_time == "⏱️ Quick (Under 100 min)":
                    params["with_runtime.lte"] = 99
                elif c_time == "⏱️ Standard (100 - 130 min)":
                    params["with_runtime.gte"] = 100
                    params["with_runtime.lte"] = 130
                else:
                    params["with_runtime.gte"] = 131

            response = requests.get(f"{BASE_URL}/discover/{endpoint}", params=params)

            if response.status_code == 200:
                results = response.json().get("results", [])
                new_candidates = [f for f in results if f.get("id") not in st.session_state.shown_movies]
                selected = []

                if len(new_candidates) >= 3:
                    selected = random.sample(new_candidates, 3)
                elif len(results) >= 3:
                    st.session_state.shown_movies = []
                    selected = random.sample(results, 3)

                if selected:
                    st.session_state.shown_movies.extend([f["id"] for f in selected])
                    st.session_state.current_results = selected
                    st.session_state.current_type = endpoint
                else:
                    st.error("Not enough results found for these specific criteria. Try changing the filters!")
            else:
                st.error("API connection failed. Please check your API Key.")

    # EĞER HENÜZ BUTONA BASILMADIYSA GÜNÜN PETEĞİNİ (DAILY HIVE) GÖSTER
    if len(st.session_state.current_results) == 0:
        if len(st.session_state.daily_hive) == 0:
            with st.spinner("Loading Today's Hive..."):
                res_trend = requests.get(f"{BASE_URL}/trending/movie/day",
                                         params={"api_key": API_KEY, "language": "en-US"})
                if res_trend.status_code == 200:
                    trend_results = res_trend.json().get("results", [])
                    if len(trend_results) >= 3:
                        # SABİTLEME BURADA: Rastgele seçmek yerine direkt ilk 3'ü alıyoruz
                        st.session_state.daily_hive = trend_results[:3]
                    else:
                        st.session_state.daily_hive = trend_results

        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🍯 Today's Hive: Trending Masterpieces</h3>",
                    unsafe_allow_html=True)
        movies_to_show = st.session_state.daily_hive
        m_type = "movie"
    else:
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🐝 Your Curated Masterpieces</h3>",
                    unsafe_allow_html=True)
        movies_to_show = st.session_state.current_results
        m_type = st.session_state.current_type

    # KARTLARI BASTIR (HEM GÜNÜN PETEĞİ HEM DE FİLTRE SONUÇLARI İÇİN ORTAK)
    if movies_to_show:
        cols = st.columns(3)
        for idx, item in enumerate(movies_to_show):
            title = item.get("title") if m_type == "movie" else item.get("name")
            overview = item.get("overview", "No overview available for this title.")
            score = item.get("vote_average", 0)
            poster_path = item.get("poster_path")

            search_query = urllib.parse.quote(f"{title} official trailer")
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

            with cols[idx]:
                with st.container(border=True):
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", use_container_width=True)
                    st.markdown(f"### {title}")
                    st.markdown(f"⭐ **{score:.1f} / 10**")
                    st.caption(overview[:140] + "..." if len(overview) > 140 else overview)
                    st.link_button("🎬 Watch Trailer", youtube_url, use_container_width=True)

# ==========================================
# 2. TAB: DIRECTOR ARCHIVE
# ==========================================
with tab_director:
    if st.session_state.selected_director_id is None:
        st.subheader("Browse: Master Directors")
        showcase = get_showcase("director")

        grid = st.columns(3)
        for idx, master in enumerate(showcase):
            with grid[idx % 3]:
                with st.container(border=True):
                    if master["photo"]:
                        st.image(f"https://image.tmdb.org/t/p/w500{master['photo']}", use_container_width=True)
                    st.button(f"{master['name']} Films", key=f"btn_d_{master['id']}",
                              on_click=set_director, args=(master["id"], master["name"]), use_container_width=True)
    else:
        if st.session_state.dir_selected_movie:
            render_movie_detail(st.session_state.dir_selected_movie, back_to_dir_list)
        else:
            st.button("🔙 Back to Directors", on_click=reset_director, key="back_dir_main")
            st.divider()
            dir_id = st.session_state.selected_director_id
            dir_name = st.session_state.selected_director_name

            with st.spinner(f"Compiling {dir_name}'s masterpieces..."):
                res = requests.get(f"{BASE_URL}/person/{dir_id}/movie_credits",
                                   params={"api_key": API_KEY, "language": "en-US"})
                if res.status_code == 200:
                    crew_data = res.json().get("crew", [])
                    unique_films = []
                    seen_ids = set()

                    for film in crew_data:
                        job = film.get("job", "")
                        if job == "Director" and film.get("release_date") and film.get("vote_count", 0) > 300:
                            if film["id"] not in seen_ids:
                                seen_ids.add(film["id"])
                                unique_films.append(film)

                    unique_films = sorted(unique_films, key=lambda x: x.get("release_date", "1900-01-01"), reverse=True)
                    st.markdown(f"### 🎬 {dir_name} Filmography ({len(unique_films)} Films)")

                    arch_cols = st.columns(3)
                    for idx, film in enumerate(unique_films):
                        with arch_cols[idx % 3]:
                            with st.container(border=True):
                                if film.get("poster_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}",
                                             use_container_width=True)
                                st.markdown(f"**{film.get('title')}**")
                                st.caption(f"🗓️ {film.get('release_date')[:4]} | ⭐ {film.get('vote_average', 0):.1f}")
                                st.button("🔍 View Details", key=f"dir_mv_{film['id']}", on_click=view_dir_movie,
                                          args=(film,), use_container_width=True)

# ==========================================
# 3. TAB: ACTOR ARCHIVE
# ==========================================
with tab_actor:
    if st.session_state.selected_actor_id is None:
        st.subheader("Browse: Iconic Actors")
        showcase = get_showcase("actor")

        grid = st.columns(3)
        for idx, master in enumerate(showcase):
            with grid[idx % 3]:
                with st.container(border=True):
                    if master["photo"]:
                        st.image(f"https://image.tmdb.org/t/p/w500{master['photo']}", use_container_width=True)
                    st.button(f"{master['name']} Films", key=f"btn_a_{master['id']}",
                              on_click=set_actor, args=(master["id"], master["name"]), use_container_width=True)
    else:
        if st.session_state.act_selected_movie:
            render_movie_detail(st.session_state.act_selected_movie, back_to_act_list)
        else:
            st.button("🔙 Back to Actors", on_click=reset_actor, key="back_act_main")
            st.divider()
            actor_id = st.session_state.selected_actor_id
            actor_name = st.session_state.selected_actor_name

            with st.spinner(f"Compiling {actor_name}'s leading roles..."):
                res = requests.get(f"{BASE_URL}/person/{actor_id}/movie_credits",
                                   params={"api_key": API_KEY, "language": "en-US"})
                if res.status_code == 200:
                    cast_data = res.json().get("cast", [])
                    unique_films = []
                    seen_ids = set()

                    for film in cast_data:
                        if film.get("order", 100) <= 5 and film.get("release_date") and film.get("vote_count", 0) > 300:
                            if film["id"] not in seen_ids:
                                seen_ids.add(film["id"])
                                unique_films.append(film)

                    unique_films = sorted(unique_films, key=lambda x: x.get("release_date", "1900-01-01"), reverse=True)
                    st.markdown(f"### 🎭 {actor_name} Leading Roles ({len(unique_films)} Films)")

                    arch_cols = st.columns(3)
                    for idx, film in enumerate(unique_films):
                        with arch_cols[idx % 3]:
                            with st.container(border=True):
                                if film.get("poster_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}",
                                             use_container_width=True)
                                st.markdown(f"**{film.get('title')}**")
                                st.caption(f"🗓️ {film.get('release_date')[:4]} | ⭐ {film.get('vote_average', 0):.1f}")
                                st.button("🔍 View Details", key=f"act_mv_{film['id']}", on_click=view_act_movie,
                                          args=(film,), use_container_width=True)
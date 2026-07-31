import streamlit as st
import requests
import random
import urllib.parse

# TMDB API Key
API_KEY = "9da4331eb5011edb49d11a04767898a2"
BASE_URL = "https://api.themoviedb.org/3"

# Page Configuration
st.set_page_config(page_title="Chobea | Cinema Curator", page_icon="🐝", layout="wide", initial_sidebar_state="expanded")

# --- CSS: WARM LIGHT MINIMAL THEME & HONEYCOMB PATTERN ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Silik Petek (Honeycomb) Arka Plan Dokusu */
    .stApp {
        background-color: #FDFBF7;
        background-image: url("data:image/svg+xml,%3Csvg width='52' height='30' viewBox='0 0 52 30' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e6a100' fill-opacity='0.04'%3E%3Cpath d='M26 0l13 7.5v15L26 30 13 22.5v-15L26 0zm0 2.309L15 9.232v11.536L26 27.691l11-6.923V9.232L26 2.309zM0 15l13 7.5v15L0 45l-13-7.5v-15L0 15zm0 2.309l-11 6.923v11.536l11 6.923 11-6.923V24.232L0 17.309zM52 15l13 7.5v15L52 45l-13-7.5v-15L52 15zm0 2.309l-11 6.923v11.536l11 6.923 11-6.923V24.232L52 17.309z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }

    /* Görseller İçin Minimalist Gölgelendirme (Ağır Çerçeveler Yerine) */
    div[data-testid="stImage"] img {
        height: 380px !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
        transition: transform 0.3s ease;
    }
    div[data-testid="stImage"] img:hover {
        transform: translateY(-5px);
    }

    /* Butonları biraz daha yumuşak hatlı yapalım */
    .stButton button, a[data-testid="baseLinkButton"] {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MEMORY & STATE MANAGEMENT ---
if "shown_movies" not in st.session_state: st.session_state.shown_movies = []
if "current_results" not in st.session_state: st.session_state.current_results = []
if "current_type" not in st.session_state: st.session_state.current_type = "movie"
if "daily_hive" not in st.session_state: st.session_state.daily_hive = []
if "my_hive" not in st.session_state: st.session_state.my_hive = []

if "selected_director_id" not in st.session_state: st.session_state.selected_director_id = None
if "selected_director_name" not in st.session_state: st.session_state.selected_director_name = None
if "dir_selected_movie" not in st.session_state: st.session_state.dir_selected_movie = None

if "selected_actor_id" not in st.session_state: st.session_state.selected_actor_id = None
if "selected_actor_name" not in st.session_state: st.session_state.selected_actor_name = None
if "act_selected_movie" not in st.session_state: st.session_state.act_selected_movie = None


# --- STATE FUNCTIONS ---
def add_to_hive(movie_dict):
    if movie_dict["id"] not in [m["id"] for m in st.session_state.my_hive]:
        st.session_state.my_hive.append(movie_dict)


def clear_hive():
    st.session_state.my_hive = []


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
        names = [
            "Christopher Nolan", "Quentin Tarantino", "David Fincher",
            "Martin Scorsese", "Denis Villeneuve", "Stanley Kubrick",
            "Steven Spielberg", "Alfred Hitchcock", "Ridley Scott",
            "James Cameron", "Hayao Miyazaki", "Bong Joon Ho"
        ]
    else:
        names = [
            "Leonardo DiCaprio", "Meryl Streep",
            "Christian Bale", "Scarlett Johansson",
            "Cillian Murphy", "Cate Blanchett",
            "Robert De Niro", "Anne Hathaway",
            "Brad Pitt", "Natalie Portman",
            "Al Pacino", "Viola Davis"
        ]

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

        search_query = urllib.parse.quote(f"{title}")
        youtube_url = f"https://www.youtube.com/results?search_query={search_query}+official+trailer"
        imdb_url = f"https://www.imdb.com/find/?q={search_query}"
        letterboxd_url = f"https://letterboxd.com/search/{search_query}/"

        b1, b2, b3 = st.columns(3)
        with b1: st.link_button("⭐ IMDb", imdb_url, help="Search on IMDB", use_container_width=True)
        with b2: st.link_button("🎬 Trailer", youtube_url, use_container_width=True)
        with b3: st.link_button("🟩 Letterboxd", letterboxd_url, help="Search on Letterboxd", use_container_width=True)

    with col2:
        st.markdown(f"<h1 style='margin-bottom:0;'>{title}</h1>", unsafe_allow_html=True)
        date = movie.get('release_date', 'Unknown')
        score = movie.get('vote_average', 0)
        st.markdown(f"<h4 style='color:gray; font-weight:normal;'>🗓️ {date[:4]} | ⭐ {score:.1f} / 10</h4>",
                    unsafe_allow_html=True)
        st.divider()
        st.write(movie.get("overview", "No overview available for this title."))


# --- SIDEBAR (SABİT 3 FİLTRE) ---
with st.sidebar:
    st.header("🍯 Filter Your Hive")
    st.caption("Adjust your basic preferences.")

    c_type = st.radio("What are you looking for?", ["🎬 Movie", "📺 TV Show & Mini-Series", "🎨 Anime & Animation"])
    c_pool = st.radio("What caliber do you prefer?", ["🏆 Cult Classics", "💎 Hidden Gems", "🍿 Popular Hits"])
    c_time = st.radio("Time Budget", ["⏱️ Any Duration", "⏱️ Quick (< 100 min)", "⏱️ Standard (100 - 130 min)",
                                      "⏱️ Marathon (130+ min)"])

# --- HERO SECTION ---
st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>🐝 Chobea</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 1.1rem; font-style: italic; margin-bottom: 2rem;'>Your personal cinema curation assistant. Curating 3 tailored masterpieces from thousands of films into your hive — grab your popcorn and watch on your favorite platforms!</p>",
    unsafe_allow_html=True)

tab_main, tab_director, tab_actor = st.tabs(["🎲 Smart Choice", "🎥 Director Archive", "🎭 Performers Archive"])

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
                if c_time == "⏱️ Quick (< 100 min)":
                    params["with_runtime.lte"] = 99
                elif c_time == "⏱️ Standard (100 - 130 min)":
                    params["with_runtime.gte"] = 100
                    params["with_runtime.lte"] = 130
                elif c_time == "⏱️ Marathon (130+ min)":
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

    if len(st.session_state.current_results) == 0:
        if len(st.session_state.daily_hive) == 0:
            with st.spinner("Loading Today's Hive..."):
                res_trend = requests.get(f"{BASE_URL}/trending/movie/day",
                                         params={"api_key": API_KEY, "language": "en-US"})
                if res_trend.status_code == 200:
                    trend_results = res_trend.json().get("results", [])
                    st.session_state.daily_hive = trend_results[:3] if len(trend_results) >= 3 else trend_results

        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🍯 Today's Hive: Trending Masterpieces</h3>",
                    unsafe_allow_html=True)
        movies_to_show = st.session_state.daily_hive
        m_type = "movie"
    else:
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🐝 Your Curated Masterpieces</h3>",
                    unsafe_allow_html=True)
        movies_to_show = st.session_state.current_results
        m_type = st.session_state.current_type

    if movies_to_show:
        cols = st.columns(3)
        for idx, item in enumerate(movies_to_show):
            title = item.get("title") if m_type == "movie" else item.get("name")
            overview = item.get("overview", "No overview available for this title.")
            score = item.get("vote_average", 0)
            poster_path = item.get("poster_path")

            search_query = urllib.parse.quote(f"{title}")
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}+official+trailer"
            imdb_url = f"https://www.imdb.com/find/?q={search_query}"
            letterboxd_url = f"https://letterboxd.com/search/{search_query}/"

            with cols[idx]:
                with st.container():
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", use_container_width=True)
                    st.markdown(f"### {title}")
                    st.markdown(f"⭐ **{score:.1f} / 10**")
                    st.caption(overview[:120] + "..." if len(overview) > 120 else overview)

                    b1, b2, b3 = st.columns(3)
                    with b1: st.link_button("⭐ IMDb", imdb_url, help="IMDB", use_container_width=True)
                    with b2: st.link_button("🎬 Trailer", youtube_url, use_container_width=True)
                    with b3: st.link_button("🟩 Letterboxd", letterboxd_url, help="Letterboxd", use_container_width=True)

                    st.button("➕ Add to My Hive", key=f"fav_{item['id']}", on_click=add_to_hive, args=(item,),
                              use_container_width=True)

    if st.session_state.my_hive:
        st.write("")
        st.write("")
        st.divider()
        st.markdown("### 🍯 My Hive (Your Selected Masterpieces)")

        export_text = "🐝 My Chobea Watchlist:\n\n"
        for idx, fav in enumerate(st.session_state.my_hive):
            f_title = fav.get("title", fav.get("name", "Unknown"))
            f_score = fav.get("vote_average", 0)
            f_date = fav.get("release_date", fav.get("first_air_date", "Unknown"))
            f_year = f_date[:4] if f_date else "Unknown"
            export_text += f"{idx + 1}. {f_title} ({f_year}) - ⭐ {f_score:.1f}/10\n"

        export_text += "\nCurated via chobea.streamlit.app"

        st.code(export_text, language="text")
        col_clear, col_info = st.columns([1, 4])
        with col_clear:
            st.button("🗑️ Clear Hive", on_click=clear_hive, use_container_width=True)
        with col_info:
            st.caption(
                "👆 Hover over the text box and click the **Copy icon** in the top right to share your list on WhatsApp!")

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
                with st.container():
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
                            with st.container():
                                if film.get("poster_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}",
                                             use_container_width=True)
                                st.markdown(f"**{film.get('title')}**")
                                st.caption(f"🗓️ {film.get('release_date')[:4]} | ⭐ {film.get('vote_average', 0):.1f}")
                                st.button("🔍 View Details", key=f"dir_mv_{film['id']}", on_click=view_dir_movie,
                                          args=(film,), use_container_width=True)

# ==========================================
# 3. TAB: ACTOR ARCHIVE (PERFORMERS)
# ==========================================
with tab_actor:
    if st.session_state.selected_actor_id is None:
        st.subheader("Browse: Iconic Performers")
        showcase = get_showcase("actor")

        grid = st.columns(3)
        for idx, master in enumerate(showcase):
            with grid[idx % 3]:
                with st.container():
                    if master["photo"]:
                        st.image(f"https://image.tmdb.org/t/p/w500{master['photo']}", use_container_width=True)
                    st.button(f"{master['name']} Films", key=f"btn_a_{master['id']}",
                              on_click=set_actor, args=(master["id"], master["name"]), use_container_width=True)
    else:
        if st.session_state.act_selected_movie:
            render_movie_detail(st.session_state.act_selected_movie, back_to_act_list)
        else:
            st.button("🔙 Back to Performers", on_click=reset_actor, key="back_act_main")
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
                            with st.container():
                                if film.get("poster_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}",
                                             use_container_width=True)
                                st.markdown(f"**{film.get('title')}**")
                                st.caption(f"🗓️ {film.get('release_date')[:4]} | ⭐ {film.get('vote_average', 0):.1f}")
                                st.button("🔍 View Details", key=f"act_mv_{film['id']}", on_click=view_act_movie,
                                          args=(film,), use_container_width=True)

st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid rgba(0,0,0,0.1); color: #888;">
        <p style="font-size: 0.75rem; margin-bottom: 5px;">*Disclaimer: Chobea is a legal cinema curation assistant. We do not host or stream copyrighted content.*</p>
        <p style="font-size: 0.75rem; margin-bottom: 0;">*This product uses the TMDB API but is not endorsed or certified by TMDB.*</p>
    </div>
""", unsafe_allow_html=True)

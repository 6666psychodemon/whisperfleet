import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Underground Type Beat Directory", layout="wide")

st.title("🎧 Underground Type Beat Directory")
st.markdown("Discovering fresh sounds. Ignoring the mainstream.")

# 1. Database Connection
def load_data():
    conn = sqlite3.connect("typebeats.db")
    # Load all columns from the new 10-column schema
    df = pd.read_sql_query("SELECT * FROM beats", conn)
    conn.close()
    return df

try:
    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    
    # Genre Filter
    genres = sorted(df['genre'].unique().tolist()) if 'genre' in df.columns else []
    selected_genre = st.sidebar.multiselect("Select Genre", genres)

    # View Count Filter
    max_views = st.sidebar.slider("Max Views", 0, 100000, 100000)

    # NEW: Free Filter
    show_free_only = st.sidebar.checkbox("Show Free Beats Only")

    # --- FILTER LOGIC ---
    filtered = df[df['views'] <= max_views]
    
    if selected_genre:
        filtered = filtered[filtered['genre'].isin(selected_genre)]
    
    if show_free_only:
        filtered = filtered[filtered['is_free'] == 1]

    # --- DISPLAY ---
    st.subheader(f"Found {len(filtered)} tracks")

    # We use 'published_time' here instead of 'upload_time_raw' to fix the error
    cols_to_show = ["artist_style", "channel_name", "views", "published_time", "url"]
    
    # Check for 'is_free' column to add a visual indicator
    if "is_free" in filtered.columns:
        filtered['Free?'] = filtered['is_free'].apply(lambda x: "✅" if x == 1 else "❌")
        cols_to_show.insert(4, "Free?")

    display_df = filtered[cols_to_show].sort_values(by="views", ascending=True)

    # Make URL clickable
    st.dataframe(
        display_df,
        column_config={
            "url": st.column_config.LinkColumn("YouTube Link"),
            "views": st.column_config.NumberColumn("Views", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )

except Exception as e:
    st.error(f"Waiting for data... (Error: {e})")
    st.info("Make sure you've run scraper.py and tagger.py at least once.")

import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# --- API Token ---
GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]

# --- Genius Song Search ---
def search_song(song_title):
    base_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    params = {"q": song_title}

    response = requests.get(base_url, headers=headers, params=params)  # ✅ Fix here
    if response.status_code != 200:
        raise Exception(f"Search failed: {response.status_code}")
    
    data = response.json()
    hits = data["response"]["hits"]

    for hit in hits:
        artist_name = hit["result"]["primary_artist"]["name"].lower()
        if "taylor swift" in artist_name:
            return hit["result"]["url"]
    return None

# --- Genius Lyrics Scraper ---
def scrape_lyrics(url):
    page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.text, "html.parser")

    # New layout
    containers = soup.select("div[class^='Lyrics__Container']")
    if containers:
        lyrics = "\n".join([c.get_text(separator="\n") for c in containers])
    else:
        lyrics_div = soup.find("div", class_="lyrics")
        lyrics = lyrics_div.get_text() if lyrics_div else ""

    return lyrics

# --- Clean Lyrics ---
def clean_lyrics(lyrics):
    lyrics = re.sub(r"\[.*?\]", "", lyrics)
    lines = lyrics.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(lines)

# --- Streamlit UI ---
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")
song_title = st.text_input("🎵 Enter Song Title", "Love Story")

if song_title:
    with st.spinner("Fetching lyrics..."):
        try:
            url = search_song(song_title)
            if url:
                raw_lyrics = scrape_lyrics(url)
                lyrics = clean_lyrics(raw_lyrics)

                st.subheader("🎧 Clean Lyrics")
                st.text_area("Lyrics", value=lyrics, height=300)

                if lyrics:
                    st.subheader("☁️ Word Cloud")
                    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(lyrics)
                    fig, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Lyrics could not be extracted. Please try a different song.")
            else:
                st.error("No results found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

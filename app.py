import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt

GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]

def search_song(song_title):
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    params = {"q": song_title}
    res = requests.get("https://api.genius.com/search", headers=headers, params=params)
    data = res.json()
    for hit in data["response"]["hits"]:
        if "taylor swift" in hit["result"]["primary_artist"]["name"].lower():
            return hit["result"]["url"]
    return None

def scrape_lyrics(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch lyrics page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")

    # First: Try grabbing from divs with class starting with Lyrics__Container
    containers = soup.select("div[class^='Lyrics__Container']")
    if containers:
        lyrics = "\n".join([c.get_text(separator="\n").strip() for c in containers])
        if lyrics.strip():
            return lyrics

    # Second: Try grabbing from the older 'lyrics' class
    old_div = soup.find("div", class_="lyrics")
    if old_div:
        lyrics = old_div.get_text(separator="\n").strip()
        if lyrics.strip():
            return lyrics

    # Third: Fallback - look through all <section> tags for large text blocks
    sections = soup.find_all("section")
    long_texts = [
        s.get_text(separator="\n").strip() for s in sections
        if len(s.get_text().split()) > 30  # crude filter to avoid nav bars etc.
    ]
    if long_texts:
        return "\n".join(long_texts)

    return None  # Nothing found

# UI
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")

song_title = st.text_input("🎵 Enter Song Title", "Love Story")

if song_title:
    with st.spinner("Fetching lyrics..."):
        try:
            url = search_song(song_title)
            if url:
                lyrics = scrape_lyrics(url)
                if lyrics:
                    st.subheader("🎧 Clean Lyrics")
                    st.text_area("Lyrics", value=lyrics, height=300)

                    st.subheader("☁️ Word Cloud")
                    wc = WordCloud(width=800, height=400, background_color="white").generate(lyrics)
                    fig, ax = plt.subplots()
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Lyrics could not be extracted. Please try a different song.")
            else:
                st.error("❌ Song not found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

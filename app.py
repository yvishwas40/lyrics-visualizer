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
    page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.text, "html.parser")
    containers = soup.select("div[class^='Lyrics__Container']")
    if not containers:
        return None
    return "\n".join([c.get_text(separator="\n").strip() for c in containers])

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

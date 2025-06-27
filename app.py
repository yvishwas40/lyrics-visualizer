import streamlit as st
import lyricsgenius
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os
# from dotenv import load_dotenv

# # --- Load .env token securely ---
# load_dotenv()
GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]

# --- Genius API Setup ---
genius = lyricsgenius.Genius(
    GENIUS_API_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)

# ✅ Set a custom browser-like User-Agent to avoid 403 errors
genius.headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/113.0.0.0 Safari/537.36"
)

# --- Helper Function ---

def clean_lyrics(lyrics):
    # Remove [Verse], [Chorus], etc.
    lyrics = re.sub(r"\[.*?\]", "", lyrics)

    # Remove contributor lines, translation credits, or metadata (e.g., first few lines if non-lyrical)
    lines = lyrics.strip().splitlines()

    # Heuristically drop top and bottom if they contain metadata
    # Remove any lines before the first actual lyric (often starts with pronouns, articles, etc.)
    start_index = 0
    for i, line in enumerate(lines):
        if re.search(r"\b(we|i|you|this|the|and|a|my|can|do|let|have|'t|could|'s)\b", line.lower()):
            start_index = i
            break

    # Remove common footer noise (e.g., last 2–4 lines with "Embed", etc.)
    end_index = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if "embed" in lines[i].lower() or "contributor" in lines[i].lower():
            end_index = i
        else:
            break

    # Keep only the clean middle part
    lines = lines[start_index:end_index]

    # Final trim and blank line removal
    cleaned = "\n".join([line.strip() for line in lines if line.strip()])

    return cleaned

# --- UI ---
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to see the lyrics and a beautiful word cloud!")

# --- Input ---
song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    with st.spinner("Fetching lyrics..."):
        try:
            song = genius.search_song(song_title, artist="Taylor Swift")
            if song and song.lyrics:
                cleaned_lyrics = clean_lyrics(song.lyrics)

                st.subheader("🎧 Clean Lyrics")
                st.text_area("Lyrics", value=cleaned_lyrics, height=300)

                # --- Word Cloud ---
                st.subheader("☁️ Word Cloud")
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color="white",
                    colormap="twilight"
                ).generate(cleaned_lyrics)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.error("No lyrics found for this song.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

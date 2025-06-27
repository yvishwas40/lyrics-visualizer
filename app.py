import streamlit as st
import lyricsgenius
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Genius API Setup ---
GENIUS_API_TOKEN = "ROnXjA5NJpAIXfQlKBq4Fz7yigs3LqaEBS6wPvV6i2M6HXqZgpqQaijX6TfbblB-"
genius = lyricsgenius.Genius(GENIUS_API_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

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
            if song:
                st.subheader("🎧 Lyrics")
                st.text_area("Lyrics", value=song.lyrics, height=300)

                # --- Word Cloud ---
                st.subheader("☁️ Word Cloud")
                wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="twilight") \
                    .generate(song.lyrics)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.error("No lyrics found for this song.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

import streamlit as st
import asyncio
from base64 import b64encode
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

# Function to display video in Streamlit
def display_video(video_path):
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_url = f"data:video/mp4;base64,{b64encode(video_bytes).decode()}"
            st.video(video_url)
    except FileNotFoundError:
        st.error("Video file not found. Please try again.")

# Function to generate the video from the topic
async def generate_video_from_topic(topic):
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    # Generate script
    response = generate_script(topic)
    if not response:
        st.error("Failed to generate script. Please try again.")
        return
    st.success("Script generated successfully!")
    st.write(f"**Generated Script:** {response}")

    # Generate audio
    await generate_audio(response, SAMPLE_FILE_NAME)

    # Generate timed captions
    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)

    # Generate search terms and video URLs
    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    if search_terms:
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
        background_video_urls = merge_empty_intervals(background_video_urls)
    else:
        st.error("Failed to generate background video. Please try again.")
        return

    # Render final video
    if background_video_urls:
        output_video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
        st.success("Video rendered successfully!")
        st.write("**Final Video:**")
        display_video(output_video)
    else:
        st.error("Failed to render video. Please try again.")

# Streamlit frontend
st.title("Text-to-Video Generator")
st.write("Enter a topic to generate a script and create a video!")

# User input
topic = st.text_input("Enter a topic:", placeholder="e.g., Fruits, AI, or Nature")

if st.button("Generate Video"):
    if topic.strip():
        st.info("Processing your request. Please wait...")
        asyncio.run(generate_video_from_topic(topic))
    else:
        st.error("Please enter a valid topic!")

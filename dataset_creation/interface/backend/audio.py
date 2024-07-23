import streamlit as st


def load_audio(identifier, dataset: str) -> str:
    audio_url = st.secrets["AUDIO_URL"]
    return audio_url + f"/{dataset}/{identifier}.mp3"


def load_musiccaps_audio(identifier) -> str:
    return load_audio(identifier, "musiccaps")


def load_sdd_audio(identifier) -> str:
    return load_audio(identifier, "sdd")

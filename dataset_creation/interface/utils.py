import zipfile
from pathlib import Path
from typing import Optional

import requests
import streamlit as st


def _chunked_download(url: str, target_file: Path | str, chunk_size: int = 8192):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    target_file.parent.mkdir(parents=True, exist_ok=True)
    total_size = int(r.headers.get("content-length", 0)) // (1024 * 1024)
    download_bar = st.progress(0, f"Downloading... 0/{total_size} MiB")
    with open(target_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            current_size = f.tell() // (1024 * 1024)
            download_bar.progress(
                current_size / total_size,
                f"Downloading... {current_size}/{total_size} MiB",
            )


def _full_download(url: str, target_file: Path | str):
    r = requests.get(url)
    r.raise_for_status()
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "wb") as f:
        f.write(r.content)


def set_page_config():
    st.set_page_config(
        page_title="Music Question Answering App",
        page_icon="🎵",
        initial_sidebar_state="collapsed",
    )


def redirect_if_no_session_state():
    if "PROLIFIC_PID" not in st.session_state:
        st.switch_page("welcome.py")


def page_setup():
    """Common setup logic for all subpages. Must be called at the beginning of each page."""
    set_page_config()
    redirect_if_no_session_state()
    st.query_params["PROLIFIC_PID"] = st.session_state["PROLIFIC_PID"]

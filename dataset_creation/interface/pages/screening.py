import streamlit as st

from backend.database import add_participant
from utils import page_setup

page_setup()

st.title("Welcome to the Music Question Answering App!", anchor=False)
st.header("Screening Questions", anchor=False)

st.radio(
    "Do you have any hearing loss or hearing difficulties?",
    ["Yes", "No", "Rather not say"],
    index=None,
    key="hearing_loss",
)

st.radio(
    "Do you have any language related disorders?",
    [
        "Reading difficulty",
        "Writing difficulty",
        "Other language related disorder",
        "None",
        "Not applicable",
    ],
    index=None,
    key="language_disorders",
)

st.multiselect(
    "Which of the following languages are you fluent in?",
    [
        "English",
        "French",
        "German",
        "Spanish",
        "Italian",
        "Portuguese",
        "Russian",
        "Chinese",
        "Japanese",
        "Korean",
        "Arabic",
        "Hindi",
        "Other",
        "Rather not say",
    ],
    key="fluency",
)

st.multiselect(
    "Do you actively engage as any of the following?",
    [
        "Influencer",
        "Blogger",
        "Video content creator",
        "Musician",
        "Artist",
        "Designer",
        "Photographer",
        "Travel guide writer",
        "AI creative",
        "Engaged online community member",
        "Prompt engineering",
        "None of the above",
        "Actor",
    ],
    key="engagement",
)

can_advance = all(
    st.session_state[key]
    for key in ["fluency", "hearing_loss", "language_disorders", "engagement"]
)
next_page = st.button("Continue", type="primary", disabled=not can_advance)
if next_page:
    fluent_in_english = "English" in st.session_state["fluency"]
    is_musician = "Musician" in st.session_state["engagement"]
    no_language_disorders = st.session_state["language_disorders"] == "None"
    no_hearing_loss = st.session_state["hearing_loss"] == "No"
    add_participant(
        database_url=st.secrets["DATABASE_URL"],
        participant_id=st.session_state["PROLIFIC_PID"],
        study_id=st.session_state.get("STUDY_ID"),
        fluent_in_english=fluent_in_english,
        no_hearing_loss=no_hearing_loss,
        no_language_disorders=no_language_disorders,
        musician=is_musician,
    )
    st.switch_page("pages/instructions.py")

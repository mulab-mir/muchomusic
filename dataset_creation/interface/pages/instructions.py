import streamlit as st
from backend.audio import load_sdd_audio
from backend.database import add_completion_code, participant_passed_comprehension_check
from utils import page_setup


def eval_comprehension_check():
    correct_1 = st.session_state["correct_1"]
    distractor1 = st.session_state["distractor1"]
    distractor2 = st.session_state["distractor2"]
    correct_2 = st.session_state["correct_2"]
    if correct_1 and correct_2 and not (distractor1 or distractor2):
        st.session_state["comprehension_check_passed"] = True
    elif (
        "comprehension_check_passed" in st.session_state
        and not st.session_state["comprehension_check_passed"]
    ):
        st.session_state["participation_failed"] = True
    else:
        st.session_state["comprehension_check_passed"] = False


page_setup()

st.title("Welcome to the Music Question Answering App!", anchor=False)

st.header("Instructions", anchor=False)

st.write(
    """
    You will be presented with a short music clip and a multiple choice
    question about the clip.

    1. Listen to the clip carefully. Headphones are recommended.
    2. Read the question and answer options carefully.
    2. Tick all options that you think correctly answer the question OR skip the question if you cannot answer it.
    If you think the question is not valid, choose "skip" --> "There is something wrong with this question" 

    Each question will have four possible answers. Some of these are correct,
    others are distractors, intended to make the task more
    challenging.
    """
)

st.warning(
    """You should pay particular attention to distractors that are similar to
    the correct answer.
    """,
    icon="⚠️",
)

audio = load_sdd_audio("24018")
error_text = """Incorrect!

Please select only answers containing actions you should always do, **NOT** optional ones.

*Hint: There are two correct statements and two distractors.*
"""

with st.expander("Show/hide example question", expanded=True):
    st.subheader("Example Question", anchor=False)

    st.audio(audio)

    st.info(
        """
        For this example, we have already marked the correct answer for you.
        Hover over the ❓ next to the options to see why they are correct or
        incorrect.
        """,
        icon="ℹ️",
    )
    st.markdown("#### How does the structure of the melody change throughout the song?")
    st.markdown(
        "☐️ It's a 90s dance pop song",
        help="This fits the music clip but is not relevant to the question",
    )
    st.markdown(
        "☑ The base melody stays the same, and other melodies are layered on top",
        help="This is the correct answer",
    )
    st.markdown(
        "☐️ The song uses acoustic instruments",
        help="This is both incorrect and unrelated to the question",
    )
    st.markdown(
        "☐️ The entire melody changes every verse",
        help="This is incorrect but related to the question",
    )

with st.form("Comprehension check form", clear_on_submit=True):
    st.subheader(
        "Based on the instructions above, what should you ALWAYS do?",
        anchor=False,
    )
    options = [
        ("I should listen to the clip carefully", "correct_1"),
        ("I should listen again without headphones", "distractor1"),
        ("I can replay the audio clip as many times as I like", "distractor2"),
        ("I should pay attention to the distractors", "correct_2"),
    ]
    for option, label in options:
        st.checkbox(
            option,
            key=label,
            disabled=st.session_state.get("participation_failed", False),
        )
    error_container = st.empty()
    submitted = st.form_submit_button(
        "Submit",
        type="primary",
        disabled=st.session_state.get("participation_failed", False),
        on_click=eval_comprehension_check,
    )


def _show_participation_failed():
    st.error("Failed comprehension check a second time!")
    url = st.secrets["PROLIFIC"]["return_url"]
    code = st.secrets["PROLIFIC"]["cc_comprehension_check_fail"]
    add_completion_code(
        st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"], code
    )
    st.link_button(
        "End survey and go back",
        url + code,
        type="primary",
    )


if submitted:
    if st.session_state.get("participation_failed", False):
        _show_participation_failed()
    elif st.session_state.get("comprehension_check_passed", False):
        st.success("Correct!")
        participant_passed_comprehension_check(
            st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
        )
        st.switch_page("pages/questionnaire.py")
    else:
        with error_container:
            st.error(error_text)

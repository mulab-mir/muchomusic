import os
import random
import time

import streamlit as st

from backend.audio import load_sdd_audio, load_musiccaps_audio
from backend.database import (
    add_completion_code,
    get_item_for_annotation,
    add_annotation,
    num_annotations_for_participant,
)
from utils import page_setup

page_setup()

DEBUG = os.environ.get("DEBUG")
MAX_QUESTIONS = int(os.environ.get("MAX_QUESTIONS", 10))


def _set_annotation_item():
    question, annotation_id = get_item_for_annotation(
        st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
    )
    st.session_state["question"] = question
    st.session_state["annotation_id"] = annotation_id


def _update_tracking(time_delta):
    st.session_state["time_deltas"].append(time_delta)
    st.session_state["time"] = time.time()
    st.session_state["question_ctr"] = num_annotations_for_participant(
        st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
    )
    st.session_state["annotation_id"] = None


def evaluate_check_boxes():
    answers = [
        i
        for i, chk_box in enumerate(
            (
                st.session_state.correct,
                st.session_state.incorrect_but_related,
                st.session_state.correct_but_unrelated,
                st.session_state.unrelated_and_incorrect,
            )
        )
        if chk_box
    ]
    answer_str = ", ".join([str(a) for a in answers])
    add_annotation_and_advance(answer_str)


def add_annotation_and_advance(answer):
    time_delta = time.time() - st.session_state["time"]
    add_annotation(
        st.secrets["DATABASE_URL"],
        st.session_state["annotation_id"],
        answer,
        time_delta,
    )
    _update_tracking(time_delta)


def check_box_form(question, audio):
    answers = [
        "correct",
        "incorrect_but_related",
        "correct_but_unrelated",
        "unrelated_and_incorrect",
    ]
    choices = [
        question.correct_answer,
        question.distractor_1,
        question.distractor_2,
        question.distractor_3,
    ]
    with st.form("Test", clear_on_submit=True):
        options = [i for i in range(len(choices))]
        random.shuffle(options)
        _display_question_and_audio(question.question, audio)
        st.caption(
            "_Tick all correct answers to the question or press skip if you are not sure how to answer._"
        )

        for option in options:
            st.checkbox(choices[option], key=answers[option])
        st.form_submit_button(on_click=evaluate_check_boxes, type="primary")
        with st.popover("Skip"):
            st.form_submit_button(
                "I can’t answer this question",
                type="primary",
                on_click=add_annotation_and_advance,
                args=["Can't answer"],
            )
            st.form_submit_button(
                "There’s something wrong with this question",
                type="primary",
                on_click=add_annotation_and_advance,
                args=["Odd question"],
            )


def _display_question_and_audio(question, audio):
    st.audio(audio)
    st.subheader(question, anchor=False)


if "annotation_id" not in st.session_state:
    st.session_state["error"] = None
    st.session_state["time"] = time.time()
    st.session_state["time_deltas"] = []
    st.session_state["question_ctr"] = num_annotations_for_participant(
        st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
    )
    st.session_state["annotation_id"] = None
if st.session_state["question_ctr"] >= MAX_QUESTIONS:
    # print("Switching to end page")
    add_completion_code(
        st.secrets["DATABASE_URL"],
        st.session_state["PROLIFIC_PID"],
        st.secrets["PROLIFIC"]["cc_success"],
    )
    st.switch_page("pages/survey_end.py")
elif st.session_state["annotation_id"] is None:
    _set_annotation_item()

if DEBUG:
    with st.sidebar:
        st.write(st.session_state)

question = st.session_state.question
if question.dataset == "sdd":
    audio = load_sdd_audio(question.dataset_identifier)
else:
    audio = load_musiccaps_audio(question.dataset_identifier)

if DEBUG:
    with st.expander("Debug"):
        st.write(question)

check_box_form(question, audio)

if st.session_state["error"]:
    st.error(st.session_state["error"])
    st.session_state["error"] = None

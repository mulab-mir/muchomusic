import streamlit as st

from backend.database import get_participant
from utils import set_page_config


def load_participant_info_sheet():
    with open("interface/participant_information_sheet.md") as f:
        return f.read()


set_page_config()

st.title("Welcome to the Music Question Answering App!", anchor=False)
st.write(
    """
    This is a short questionnaire to collect data for a research project.
    You will be presented with a short music clip.
    You will then be asked to answer a multiple choice question.
    """
)

query_params = st.query_params.to_dict()

if "PROLIFIC_PID" in query_params:
    st.session_state["PROLIFIC_PID"] = query_params["PROLIFIC_PID"]
    st.session_state["STUDY_ID"] = query_params.get("STUDY_ID")
    st.session_state["SESSION_ID"] = query_params.get("SESSION_ID")
    st.info(
        f"We have detected your Prolific ID. Your ID is: {st.session_state['PROLIFIC_PID']}"
    )
elif "PROLIFIC_PID" in st.session_state and st.session_state["PROLIFIC_PID"]:
    st.info(
        f"We have received your Prolific ID. Your ID is: {st.session_state['PROLIFIC_PID']}"
    )
    # if we got redirected after a refresh, we need to re-add the query params
    st.query_params["PROLIFIC_PID"] = st.session_state["PROLIFIC_PID"]
else:
    st.session_state["PROLIFIC_PID"] = None
    st.session_state["STUDY_ID"] = None
    st.session_state["SESSION_ID"] = None
    st.warning("We have not received your Prolific ID. Please enter it below.")
    id_input = st.text_input("Prolific ID", max_chars=24)
    if id_input:
        st.session_state["PROLIFIC_PID"] = id_input
        st.info(f"Your ID is: {st.session_state['PROLIFIC_PID']}")

if (
    participant := get_participant(
        st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
    )
) is not None:
    if participant.completion_code:
        st.switch_page("pages/survey_end.py")
    elif participant.passed_comprehension_check:
        st.switch_page("pages/questionnaire.py")
    else:
        st.switch_page("pages/instructions.py")

st.header("Participant Information Sheet", anchor=False)

with st.container(border=True):
    st.markdown(load_participant_info_sheet())

st.header("Informed Consent", anchor=False)

consent_statements = [
    "1. I confirm that I have read the Participant Information Sheet dated 19.02.2024 version 0.2 for the above study; or it has been read to me. I have had the opportunity to consider the information, ask questions and have had these answered satisfactorily.",
    "2. I understand that my participation is voluntary and that I am free to stop taking part in the study at any time without giving any reason and without my rights being affected.",
    "3. I understand that my data will be accessed by the research team.",
    "4. I understand that my data will be securely stored in secure database server within the UK and in accordance with the data protection guidelines of the Queen Mary University of London in fully anonymised form.",
    "5. I understand that I can access the information I have provided and request destruction of that information at any time prior to 12.04.24. I understand that following 12.04.24, I will not be able to request withdrawal of the information I have provided.",
    "6. I understand that the researcher will not identify me in any publications and other study outputs using personal information obtained from this study.",
    "7. I understand that the information collected about me will be used to support other research in the future, and it may be shared in anonymised form with other researchers.",
    "8. I agree to take part in the above study.",
]

for i, statement in enumerate(consent_statements):
    st.checkbox(statement, key=f"consent_{i}")

can_continue = (
    all(st.session_state[f"consent_{i}"] for i in range(len(consent_statements)))
    and st.session_state["PROLIFIC_PID"]
)

start = st.button(
    "Start",
    disabled=not can_continue,
    type="primary",
)
if start:
    st.switch_page("pages/screening.py")

with st.expander("Stop without completing", expanded=False):
    url = st.secrets["PROLIFIC"]["return_url"]
    completion_code = st.secrets["PROLIFIC"]["cc_no_consent"]
    st.warning("You have chosen to stop without completing the study.")
    st.link_button(
        "Return to Prolific",
        url + completion_code,
        type="primary",
    )

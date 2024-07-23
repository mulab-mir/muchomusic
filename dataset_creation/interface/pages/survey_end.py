import streamlit as st

from utils import page_setup
from backend.database import get_participant

page_setup()

st.header("Thank you for participating in this study!")
st.write(
    """
    :pray: Your participation is greatly appreciated.
    """
)
st.balloons()

url = st.secrets["PROLIFIC"]["return_url"]
participant = get_participant(
    st.secrets["DATABASE_URL"], st.session_state["PROLIFIC_PID"]
)
completion_code = participant.completion_code

st.info(
    f"Please click the button below to return to Prolific and automatically submit your completion code."
)

st.link_button(
    "Return to Prolific",
    url + completion_code,
    type="primary",
    use_container_width=True,
)

with st.expander("In case you need to copy the code manually"):
    st.write("Your completion code is:")
    st.code(completion_code)

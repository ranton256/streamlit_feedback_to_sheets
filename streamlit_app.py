import logging
import random

import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Streamlit Feedback to Sheets Example",
    page_icon=":rocket:",
    layout="wide",
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("main")

st.header("Save Streamlit feedback to Google sheets")

st.markdown("""This app demonstrates using collecting user feedback from a Streamlit app into a Google sheet, 

- It uses the [st.feedback](https://docs.streamlit.io/develop/api-reference/widgets/st.feedback) widget 
- It uses the [gsheets-connection](https://github.com/streamlit/gsheets-connection) package to save and load feedback,\
  making it easy to collect user feedback without setting up a database as a backend.

The code is available at <https://github.com/ranton256/streamlit_feedback_to_sheets>.

""")


# Create a connection object.
def create_gsheets_connection():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"Unable to connect to storage: {e}")
        logger.error(e, stack_info=True, exc_info=True)
        return None


def append_row(df, row):
    return pd.concat([
        df,
        pd.DataFrame([row], columns=row.index)]
    ).reset_index(drop=True)


def get_user_email():
    exp_user_email = ''
    if st.experimental_user.email:
        exp_user_email = st.experimental_user.email
    logger.debug(f"Your exp_user_email is {exp_user_email}")
    return exp_user_email


def handle_clear_feedback():
    if st.button("Clear"):
        st.session_state.pop('my_random_id')
        st.rerun()


def display_rating_feedback(rating):
    sentiment_mapping = ["one", "two", "three", "four", "five"]
    if rating is not None:
        st.markdown(f"You selected {sentiment_mapping[rating]} star(s).")
        return rating + 1
    return rating


def submit_feedback(df, conn, record, new_row, rating):
    if rating is None:
        st.write("Please select a rating")
    else:
        logger.debug(f"Submitting record: {record}, row={new_row}")
        df = append_row(df, new_row)
        request_id = record['request_id']
        _ = conn.update(
            worksheet="Sheet1",
            data=df,
        )
        logger.info(f"Submitted feedback for request_id={request_id}")
        st.cache_data.clear()
        st.rerun()


def show_ui():
    conn = create_gsheets_connection()
    if not conn:
        return

    logger.info("Connected to Google Sheets.")
    df = conn.read()

    with st.expander("Expand to see feedback submitted. Warning! These are not curated!"):
        st.subheader("Feedback Received")
        st.dataframe(df)

    if 'my_random_id' not in st.session_state:
        st.session_state['my_random_id'] = random.randint(1, 10000000)

    request_id = st.session_state['my_random_id']
    logger.debug(f"request_id={request_id}")

    with st.sidebar:
        mask = df['request_id'].isin([request_id])
        found = mask.any()
        if found:
            logger.debug(f"Found record for request_id={request_id}")
            st.write("Thanks for your feedback!")
            handle_clear_feedback()

        with st.form(key="feedback"):
            logger.debug(f"New record for request_id={request_id}")
            st.write("Please rate your experience:")
            rating = st.feedback("stars")
            rating = display_rating_feedback(rating)

            comment = st.text_input("Comment", "")
            email = st.text_input("[Optional]: Enter your Email if you would like to discuss", "")

            exp_user_email = get_user_email()
            record = {'request_id': request_id, 'rating': rating, 'comment': comment, 'exp_user_email': exp_user_email,
                      'email': email}
            new_row = pd.Series(record)

            if st.form_submit_button("Submit", disabled=found):
                submit_feedback(df, conn, record, new_row, rating)


show_ui()

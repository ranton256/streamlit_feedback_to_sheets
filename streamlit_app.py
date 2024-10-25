from traceback import TracebackException
import random

import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
        page_title="Streamlit Feedback to Sheets Example",
        page_icon=":rocket:",
        layout="wide",
    )

# Create a connection object.
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.write(f"Unable to connect to storage: {e}")
    conn = None
    print("Connection failed")
    TracebackException.from_exception(e).print()


df = conn.read()

st.dataframe(df)


def append_row(df, row):
    return pd.concat([
        df,
        pd.DataFrame([row], columns=row.index)]
    ).reset_index(drop=True)


if 'my_random_id' not in st.session_state:
    st.session_state['my_random_id'] = random.randint(1, 10000000)

request_id = st.session_state['my_random_id']
st.write(f"request_id={request_id}")


with st.sidebar:
    mask = df['request_id'].isin([request_id])
    found = mask.any()
    if found:
        st.write("Thanks for your feedback!")
        if st.button("Clear"):
            st.session_state.pop('my_random_id')
            st.rerun()

    with st.form(key="feedback"):
        sentiment_mapping = ["one", "two", "three", "four", "five"]
        rating = st.feedback("stars")
        if rating is not None:
            st.markdown(f"You selected {sentiment_mapping[rating]} star(s).")
            rating += 1

        comment = st.text_input("Comment", "")
        email = st.text_input("[Optional]: Enter your Email if you would like to discuss", "")

        exp_user_email = ''
        if st.experimental_user.email:
            exp_user_email = st.experimental_user.email
        st.write(f"Your exp_user_email is {exp_user_email}")
        record = {'request_id': request_id, 'rating': rating, 'comment': comment, 'exp_user_email': exp_user_email, 'email': email}
        new_row = pd.Series(record)

        if st.form_submit_button("Submit", disabled=found):
            if rating is None:
                st.write("Please select a rating")
            else:
                print(f"Submitting record: {record}, row={new_row}")
                df = append_row(df, new_row)

                print("Submitted.")
                df = conn.update(
                    worksheet="Sheet1",
                    data=df,
                )
                st.cache_data.clear()
                st.rerun()

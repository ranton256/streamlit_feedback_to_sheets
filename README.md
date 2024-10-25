## Overview

**Try out this app at [https://feedback2sheets.streamlit.app/](https://feedback2sheets.streamlit.app/)**


This is an example of using the [st.feedback](https://docs.streamlit.io/develop/api-reference/widgets/st.feedback) widget to save user feedback to rows in a Google sheet so that 
it is easy to collect user feedback without setting up a database as a backend.

It uses the [gsheets-connection](https://github.com/streamlit/gsheets-connection) package for saving and loading the feedback.

And to make it a bit more interesting it shows the feedback in a dataframe in the app so you can see it as it works.

Access to the Google sheets is via the Sheets API access which must be enabled through the Google Developers Console.
You also must create a service account, and share the spreadsheet you want to use with the account's email.

The information for the Google Sheets API and the service account and spreadsheet URL must all be configured in secrets.toml for your app.

This setup process is documented in the gsheets-connection README at <https://github.com/streamlit/gsheets-connection>.

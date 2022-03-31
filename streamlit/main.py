import os

import numpy as np
import pandas as pd
import psycopg2
from joblib import load

import streamlit as st

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()

# Perform query; defaults to grabbing the ufc_table.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def load_data(query="SELECT * FROM ufc_table LIMIT 10"):
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=columns).fillna(np.nan)


# Load model.
# TODO: Add other classifiers.
def load_model(classifier="../Resources/clf.joblib"):
    return load(os.path.join(classifier))


# Predict who wins the fight.
def predict(df):
    # If dataframe column contains Winner then drop it
    if "Winner" in df.columns:
        df = df.drop(columns=["Winner"])
    return clf.predict(df), clf.predict_proba(df)


# Create column with fight matchup.
def create_fight_matchup(df):
    df["Fight_Matchup"] = df["B_Name"] + " vs. " + df["R_Name"]
    return df


# Load data from database
ufc_df = load_data()
ufc_df = create_fight_matchup(ufc_df)

# Load Model
clf = load_model()

# App Layout
# ------------------------- #
# Sidebar
# ----- #
with st.sidebar:
    st.sidebar.header("Options")
    # Model Selection
    st.sidebar.subheader("Model Selection")
    model_selection = st.sidebar.selectbox(
        "Classifier",
        [
            "VotingClassifier",
            "GradientBoostingClassifier",
            "RandomForestClassifier",
            "MLPClassifier",
            "SVC",
            "XGBClassifier",
        ],
    )
    # Data Selection
    st.sidebar.subheader("Prediction Options")
    data_selection = st.sidebar.selectbox(
        "Data Selection",
        ["Upcoming Fights", "Fighter vs. Fighter", "Create your own fighter",],
    )

    # If user selected "Upcoming Fights" then allow user to pick and predict a upcoming fight.
    if data_selection == "Upcoming Fights":
        upcoming_fight_matchup = st.sidebar.selectbox(
            "Upcoming Fights", ufc_df["Fight_Matchup"],
        )

    # Visualization Selection
    st.sidebar.subheader("Visualizations")
    win_rate_by = st.sidebar.selectbox(
        "Win Rate By", ["Age", "Height", "Weight", "Stance"]
    )


# Main page
# ----- #
st.title("UFC Fighter Prediction")
st.header("Predict Fight (Database)")
fight_selection = ufc_df.iloc[[0]]
prediction, pred_proba = predict(fight_selection)
st.write(prediction)
st.write(pred_proba)


# # Check if the original dataframe has the same results as database.
# # ----- #
# # Load DataFrame
# ufc_df = load("../Resources/clean_scraped_data.joblib")
# st.header("Predict Fight (saved DataFrame)")
# # Predict first fight
# fight_selection = ufc_df.iloc[[0]]
# prediction, pred_proba = predict(fight_selection)
# st.write(prediction)
# st.write(pred_proba)

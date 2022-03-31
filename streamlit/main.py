import os

import numpy as np
import pandas as pd
import psycopg2
from joblib import load

import streamlit as st

# Load model. # TODO: Add other classifiers.
def load_model(classifier="../Resources/clf.joblib"):
    return load(os.path.join(classifier))


# Predict who wins the fight.
def predict(df):
    # If dataframe column contains Winner then drop it
    if "Winner" in df.columns:
        df = df.drop(columns=["Winner"])
    return clf.predict(df), clf.predict_proba(df)


# Load Model
clf = load_model()

# Load DataFrame
ufc_df = load("../Resources/clean_scraped_data.joblib")

# Main page
# -------------------------#
st.title("UFC Fighter Prediction")
# Predict fight based on fighter stats
st.header("Predict Fight")

# Predict first fight
fight_selection = ufc_df.iloc[[0]]
prediction, pred_proba = predict(fight_selection)
st.write(prediction)
st.write(pred_proba)


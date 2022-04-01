import os
import numpy as np
import pandas as pd
import psycopg2
from joblib import load
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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


# Load data from database.
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
    elif data_selection == "Fighter vs. Fighter":
        # TODO: Fighter vs. Fighter
        blue_fighter = st.sidebar.selectbox("Blue Fighter", ufc_df["B_Name"].unique())
        red_fighter = st.sidebar.selectbox("Red Fighter", ufc_df["R_Name"].unique())
    elif data_selection == "Create your own fighter":
        # TODO: Create your own fighter
        # I am testing the different Streamlit widgets:
        st.sidebar.subheader("First Fighter")
        red_fighter_age_2 = st.sidebar.number_input(
            "Insert age 1", min_value=18, max_value=75, value=18
        )
        red_fighter_age = st.sidebar.slider("Fighter 1 Age", 18, 75, 25)
        red_fighter_weight = st.sidebar.slider("Fighter 1 Weight (lb)", 115, 265, 150)
        red_fighter_stance = st.sidebar.selectbox(
            "Fighter 1 Stance", ufc_df["R_Stance"].head(5)
        )
        st.sidebar.subheader("Second Fighter")
        blue_fighter_age_2 = st.sidebar.number_input(
            "Insert age 2", min_value=18, max_value=75, value=18
        )
        blue_fighter_age = st.sidebar.slider("Fighter 2 Age", 18, 75, 25)
        blue_fighter_weight = st.sidebar.slider("Fighter 2 Weight (lb)", 115, 265, 150)
        blue_fighter_stance = st.sidebar.selectbox(
            "Fighter 2 Stance", ufc_df["R_Stance"].head(5)
        )
    # Visualization Selection
    st.sidebar.subheader("Visualizations")
    win_rate_by = st.sidebar.selectbox(
        "Win Rate By", ["Age", "Height", "Weight Class", "Stance"]
    )


# Main page
# ----- #
st.title("UFC Fighter Prediction")
st.header("Predict Fight (Database)")

# TODO: This should be refactored at some point in the future.
if data_selection == "Upcoming Fights":
    fight_detail = ufc_df[ufc_df["Fight_Matchup"] == upcoming_fight_matchup]
    blue_name = fight_detail["B_Name"].iloc[0]
    blue_age = fight_detail["B_Age"].iloc[0]
    blue_height = fight_detail["B_Height"].iloc[0]
    blue_weight = fight_detail["B_Weight"].iloc[0]
    blue_reach = fight_detail["B_Reach"].iloc[0]
    blue_stance = fight_detail["B_Stance"].iloc[0]
    red_name = fight_detail["R_Name"].iloc[0]
    red_age = fight_detail["R_Age"].iloc[0]
    red_height = fight_detail["R_Height"].iloc[0]
    red_weight = fight_detail["R_Weight"].iloc[0]
    red_reach = fight_detail["R_Reach"].iloc[0]
    red_stance = fight_detail["R_Stance"].iloc[0]

    # Predict fight.
    prediction, pred_proba = predict(fight_detail)

    # Display results of prediction.
    if prediction == "Blue":
        predicted_winner = blue_name
    elif prediction == "Red":
        predicted_winner = red_name

    # Display probability of prediction.
    st.write(f"The predicted winner of this fight is: {predicted_winner}.")
    st.write(
        f"The predicted probability of the winner being {blue_name} is: {round(pred_proba[0][0] * 100, 2)}%"
    )
    st.write(
        f"The predicted probability of the winner being {red_name} is: {round(pred_proba[0][1] * 100, 2)}%"
    )

    # Display statistics of selected fighter.
    col1, col2 = st.columns(2)
    col1.subheader(f"{blue_name}")
    col1.write(f"Age: {blue_age}")
    col1.write(f"Height: {blue_height}")
    col1.write(f"Weight: {blue_weight}")
    col1.write(f"Reach: {blue_reach}")
    col1.write(f"Stance: {blue_stance}")
    col2.subheader(f"{red_name}")
    col2.write(f"Age: {red_age}")
    col2.write(f"Height: {red_height}")
    col2.write(f"Weight: {red_weight}")
    col2.write(f"Reach: {red_reach}")
    col2.write(f"Stance: {red_stance}")

elif data_selection == "Fighter vs. Fighter":
    st.subheader("Fighter vs. Fighter")
    # TODO: Predict fight.
    # TODO: Display probability of prediction.
    # TODO: Display statistics of selected fighter.
    col1, col2 = st.columns(2)
    col1.subheader(f"{blue_fighter}")
    col2.subheader(f"{red_fighter}")

    # # Get the fighter stats
    # blue_name = blue_fighter["Name"].iloc[0]
    # blue_age = blue_fighter["Age"].iloc[0]
    # blue_height = blue_fighter["Height"].iloc[0]
    # blue_weight = blue_fighter["Weight"].iloc[0]
    # blue_reach = blue_fighter["Reach"].iloc[0]
    # blue_stance = blue_fighter["Stance"].iloc[0]
    # red_name = red_fighter["Name"].iloc[0]
    # red_age = red_fighter["Age"].iloc[0]
    # red_height = red_fighter["Height"].iloc[0]
    # red_weight = red_fighter["Weight"].iloc[0]
    # red_reach = red_fighter["Reach"].iloc[0]
    # red_stance = red_fighter["Stance"].iloc[0]

    # # Put the fighter stats in a DataFrame
    # fvf_df = pd.DataFrame()
    # fvf_df["Fight_Matchup"] = blue_name + " vs. " + red_name
    # fvf_df["B_Name"] = blue_name
    # fvf_df["B_Age"] = blue_age
    # fvf_df["B_Height"] = blue_height
    # fvf_df["B_Weight"] = blue_weight
    # fvf_df["B_Reach"] = blue_reach
    # fvf_df["B_Stance"] = blue_stance
    # fvf_df["R_Name"] = red_name
    # fvf_df["R_Age"] = red_age
    # fvf_df["R_Height"] = red_height
    # fvf_df["R_Weight"] = red_weight
    # fvf_df["R_Reach"] = red_reach
    # fvf_df["R_Stance"] = red_stance

    # fvf_fight_matchup = fvf_df["Fight_Matchup"]

    # # Predict fight.
    # prediction, pred_proba = predict(fvf_fight_matchup)

    # # Display results of prediction.
    # if prediction == "Blue":
    #     predicted_winner = blue_name
    # elif prediction == "Red":
    #     predicted_winner = red_name

    # # Display probability of prediction.
    # st.write(f"The predicted winner of this fight is: {predicted_winner}.")
    # st.write(
    #     f"The predicted probability of the winner being {blue_name} is: {round(pred_proba[0][0] * 100, 2)}%"
    # )
    # st.write(
    #     f"The predicted probability of the winner being {red_name} is: {round(pred_proba[0][1] * 100, 2)}%"
    # )

    # Display statistics of selected fighter.
    # col1, col2 = st.columns(2)
    # col1.subheader(f"{blue_name}")
    # col1.write(f"Age: {blue_age}")
    # col1.write(f"Height: {blue_height}")
    # col1.write(f"Weight: {blue_weight}")
    # col1.write(f"Reach: {blue_reach}")
    # col1.write(f"Stance: {blue_stance}")
    # col2.subheader(f"{red_name}")
    # col2.write(f"Age: {red_age}")
    # col2.write(f"Height: {red_height}")
    # col2.write(f"Weight: {red_weight}")
    # col2.write(f"Reach: {red_reach}")
    # col2.write(f"Stance: {red_stance}")

elif data_selection == "Create your own fighter":
    st.subheader("Create your own fighter")
    # TODO: Predict fight.
    # TODO: Display probability of prediction.
    # TODO: Display statistics of selected fighter.


@st.cache
def chart_data():
    chart_data = load_data("SELECT * FROM ufc_table")
    return chart_data


chart_df = chart_data()

# Win Rate By Charts
if win_rate_by == "Age":
    st.header(f"Win Rate By {win_rate_by}")

    blue_wr_age = (
        chart_df[chart_df.Winner == "Blue"]
        .groupby("B_Age_Bucket")
        .Winner.count()
        .reset_index()
    )
    red_wr_age = (
        chart_df[chart_df.Winner == "Red"]
        .groupby("R_Age_Bucket")
        .Winner.count()
        .reset_index()
    )

    fig = make_subplots(rows=2, cols=1, specs=[[{"type": "pie"}], [{"type": "pie"}]])

    fig.add_trace(
        go.Pie(
            values=red_wr_age["Winner"],
            labels=red_wr_age["R_Age_Bucket"],
            name="Red Corner",
            legendgroup="1",
            title="<b>Red Win Rate By Age</b>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            values=blue_wr_age["Winner"],
            labels=blue_wr_age["B_Age_Bucket"],
            name="Blue Corner",
            legendgroup="2",
            showlegend=True,
            title="<b>Blue Win Rate By Age</b>",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=0, r=500, t=100, b=0),
        height=900,
        width=900,
        legend_tracegroupgap=450,
        legend=dict(title="<b>Age Range (in.):</b> "),
        font=dict(size=18),
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=1.25)))
    st.plotly_chart(fig)


elif win_rate_by == "Height":
    st.header(f"Win Rate By {win_rate_by}")
    blue_wr_height = (
        chart_df[chart_df.Winner == "Blue"]
        .groupby("B_Height_Bucket")
        .Winner.count()
        .reset_index()
    )
    red_wr_height = (
        chart_df[chart_df.Winner == "Red"]
        .groupby("R_Height_Bucket")
        .Winner.count()
        .reset_index()
    )

    fig = make_subplots(rows=2, cols=1, specs=[[{"type": "pie"}], [{"type": "pie"}]])
    fig.add_trace(
        go.Pie(
            values=red_wr_height["Winner"],
            name="Red Corner",
            labels=red_wr_height["R_Height_Bucket"],
            title="<b>Red Win Rate By Height</b>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Pie(
            values=blue_wr_height["Winner"],
            name="Blue Corner",
            labels=blue_wr_height["B_Height_Bucket"],
            title="<b>Blue Win Rate By Height</b>",
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=500, t=100, b=0),
        height=900,
        width=900,
        legend=dict(title="<b>Height Range (in.):</b> "),
        font_size=18,
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=1.25)))
    st.plotly_chart(fig)

elif win_rate_by == "Weight Class":
    st.header(f"Win Rate By {win_rate_by}")
    blue_wr_weight = (
        chart_df[chart_df.Winner == "Blue"]
        .groupby("Weight_Class")
        .Winner.count()
        .reset_index()
    )
    red_wr_weight = (
        chart_df[chart_df.Winner == "Red"]
        .groupby("Weight_Class")
        .Winner.count()
        .reset_index()
    )

    fig = make_subplots(rows=2, cols=1, specs=[[{"type": "pie"}], [{"type": "pie"}]])
    fig.add_trace(
        go.Pie(
            values=red_wr_weight["Winner"],
            labels=red_wr_weight["Weight_Class"],
            name="Red Corner",
            title="<b>Red Win Rate By Weight Class</b>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            values=blue_wr_weight["Winner"],
            labels=blue_wr_weight["Weight_Class"],
            name="Blue Corner",
            title="<b>Blue Win Rate By Weight Class</b>",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=0, r=500, t=100, b=0),
        height=900,
        width=900,
        legend=dict(title="<b>Weight Classes:</b> ", x=1.1),
        font=dict(size=18),
        legend_font_size=18,
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.5)))
    st.plotly_chart(fig)

elif win_rate_by == "Stance":

    st.header(f"Win Rate By {win_rate_by}")

    fig = make_subplots(rows=2, cols=1, specs=[[{"type": "pie"}], [{"type": "pie"}]])

    blue_wr_stance = (
        chart_df[chart_df.Winner == "Blue"]
        .groupby("B_Stance")
        .Winner.count()
        .reset_index()
    )
    red_wr_stance = (
        chart_df[chart_df.Winner == "Red"]
        .groupby("R_Stance")
        .Winner.count()
        .reset_index()
    )
    fig.append_trace(
        go.Pie(
            values=red_wr_stance["Winner"],
            labels=red_wr_stance["R_Stance"],
            name="Red Corner",
            title="<b>Red Win Rate By Stance</b>",
        ),
        row=1,
        col=1,
    )

    fig.append_trace(
        go.Pie(
            values=blue_wr_stance["Winner"],
            labels=blue_wr_stance["B_Stance"],
            name="Blue Corner",
            title="<b>Blue Win Rate By Stance</b>",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=0, r=500, t=100, b=0),
        height=900,
        width=900,
        legend=dict(title="<b>Fight Stance:</b> "),
        font=dict(size=18),
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=1.25)))
    st.plotly_chart(fig)


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

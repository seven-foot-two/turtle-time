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
    # if "Winner" in df.columns:
    #    df = df.drop(columns=["Winner"])
    return clf.predict(df), clf.predict_proba(df)


# Create column with fight matchup.
def create_fight_matchup(df):
    df["Fight_Matchup"] = df["B_Name"] + " vs. " + df["R_Name"]
    return df


# Load data from database.
ufc_df = load_data()
ufc_df = create_fight_matchup(ufc_df)

fighter_agg_stats = load_data(query="SELECT * FROM fighter_agg_stats")

chart_df = load_data(
    'SELECT "R_Age_Bucket", "B_Age_Bucket", "B_Height_Bucket", "R_Height_Bucket", "B_Stance", "R_Stance", "Weight_Class", "Winner" FROM ufc_table'
)
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
        # Fighter vs. Fighter
        blue_fighter = st.sidebar.selectbox(
            "Blue Fighter", fighter_agg_stats["Name"].unique()
        )
        red_fighter = st.sidebar.selectbox(
            "Red Fighter", fighter_agg_stats["Name"].unique()
        )
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
# st.header("Predict Fight (Database)")

# TODO: This should be refactored at some point in the future.
if data_selection == "Upcoming Fights":
    st.header("Upcoming Fights")

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

    # Display results of prediction, changing different formatting for each corner (red or blue)
    if prediction == "Blue":
        predicted_winner = blue_name
    elif prediction == "Red":
        predicted_winner = red_name

    if predicted_winner == blue_name:
        winner = f'<b>The predicted winner of this fight, from <span style="color:#636EFA;">the blue corner</span>, is: <span style="color:#636EFA;font-size:20px">{predicted_winner}</span></b>'
    elif predicted_winner == red_name:
        winner = f'<b>The predicted winner of this fight, from <span style="color:#EF563B;">the red corner</span>, is: <span style="color:#EF563B;font-size:20px">{predicted_winner}</span></b>'
    st.markdown(winner, unsafe_allow_html=True)

    # Display probability of prediction.

    st.write(
        f"The predicted probability of the winner being {blue_name} is: {round(pred_proba[0][0] * 100, 2)}%"
    )
    st.write(
        f"The predicted probability of the winner being {red_name} is: {round(pred_proba[0][1] * 100, 2)}%"
    )

    # Display statistics of selected fighter.
    blue_header = f'<h1><b><span style="color:#636EFA">Blue</b></h1>'
    red_header = f'<h1><b><span style="color:#EF563B">Red</b></h1>'

    col1, col2 = st.columns(2)
    col1.markdown(blue_header, unsafe_allow_html=True)
    col1.subheader(f"{blue_name}")
    col1.write(f"Age: {blue_age}")
    col1.write(f"Height: {blue_height}")
    col1.write(f"Weight: {blue_weight}")
    col1.write(f"Reach: {blue_reach}")
    col1.write(f"Stance: {blue_stance}")
    col2.markdown(red_header, unsafe_allow_html=True)
    col2.subheader(f"{red_name}")
    col2.write(f"Age: {red_age}")
    col2.write(f"Height: {red_height}")
    col2.write(f"Weight: {red_weight}")
    col2.write(f"Reach: {red_reach}")
    col2.write(f"Stance: {red_stance}")

elif data_selection == "Fighter vs. Fighter":
    st.header("Fighter vs. Fighter")
    # Get blue & red fighters
    fighter_stats_blue = fighter_agg_stats[
        fighter_agg_stats["Name"] == blue_fighter
    ].reset_index()
    fighter_stats_red = fighter_agg_stats[
        fighter_agg_stats["Name"] == red_fighter
    ].reset_index()

    # Get the fighter stats
    blue_name = fighter_stats_blue["Name"]
    blue_age = fighter_stats_blue["Age"]
    blue_height = fighter_stats_blue["Height"]
    blue_weight = fighter_stats_blue["Weight"]
    blue_age_bucket = fighter_stats_blue["Age_Bucket"]
    blue_height_bucket = fighter_stats_blue["Height_Bucket"]
    blue_reach = fighter_stats_blue["Reach"]
    blue_stance = fighter_stats_blue["Stance"]
    blue_wins = fighter_stats_blue["Wins"]
    blue_losses = fighter_stats_blue["Losses"]
    blue_draws = fighter_stats_blue["Draws"]
    blue_no_contest = fighter_stats_blue["No_Contest"]
    blue_career_significant_strikes_landed_PM = fighter_stats_blue[
        "Career_Significant_Strikes_Landed_PM"
    ]
    blue_career_striking_accuracy = fighter_stats_blue["Career_Striking_Accuracy"]
    blue_career_significant_strike_defence = fighter_stats_blue[
        "Career_Significant_Strike_Defence"
    ]
    blue_career_takedown_average = fighter_stats_blue["Career_Takedown_Average"]
    blue_career_takedown_accuracy = fighter_stats_blue["Career_Takedown_Accuracy"]
    blue_career_takedown_defence = fighter_stats_blue["Career_Takedown_Defence"]
    blue_career_submission_average = fighter_stats_blue["Career_Submission_Average"]
    blue_knockdowns = fighter_stats_blue["Knockdowns"]

    red_name = fighter_stats_red["Name"]
    red_age = fighter_stats_red["Age"]
    red_height = fighter_stats_red["Height"]
    red_weight = fighter_stats_red["Weight"]
    red_age_bucket = fighter_stats_red["Age_Bucket"]
    red_height_bucket = fighter_stats_red["Height_Bucket"]
    red_reach = fighter_stats_red["Reach"]
    red_stance = fighter_stats_red["Stance"]
    red_wins = fighter_stats_red["Wins"]
    red_losses = fighter_stats_red["Losses"]
    red_draws = fighter_stats_red["Draws"]
    red_no_contest = fighter_stats_red["No_Contest"]
    red_career_significant_strikes_landed_PM = fighter_stats_red[
        "Career_Significant_Strikes_Landed_PM"
    ]
    red_career_striking_accuracy = fighter_stats_red["Career_Striking_Accuracy"]
    red_career_significant_strike_defence = fighter_stats_red[
        "Career_Significant_Strike_Defence"
    ]
    red_career_takedown_average = fighter_stats_red["Career_Takedown_Average"]
    red_career_takedown_accuracy = fighter_stats_red["Career_Takedown_Accuracy"]
    red_career_takedown_defence = fighter_stats_red["Career_Takedown_Defence"]
    red_career_submission_average = fighter_stats_red["Career_Submission_Average"]
    red_knockdowns = fighter_stats_red["Knockdowns"]

    fvf_df = pd.DataFrame(columns=ufc_df.columns)
    fvf_df["B_Name"] = blue_name
    fvf_df["B_Age"] = blue_age
    fvf_df["B_Height"] = blue_height
    fvf_df["B_Weight"] = blue_weight
    fvf_df["B_Reach"] = blue_reach
    fvf_df["B_Stance"] = blue_stance
    fvf_df["B_Age_Bucket"] = blue_age_bucket
    fvf_df["B_Height_Bucket"] = blue_height_bucket
    fvf_df["B_Wins"] = blue_wins
    fvf_df["B_Draws"] = blue_draws
    fvf_df["B_No_Contest"] = blue_no_contest
    fvf_df[
        "B_Career_Significant_Strikes_Landed_PM"
    ] = blue_career_significant_strikes_landed_PM
    fvf_df["B_Career_Striking_Accuracy"] = blue_career_striking_accuracy
    fvf_df["B_Career_Takedown_Average"] = blue_career_submission_average
    fvf_df["B_Career_Takedown_Accuracy"] = blue_career_takedown_accuracy
    fvf_df["B_Career_Takedown_Defence"] = blue_career_takedown_defence
    fvf_df["B_Career_Submission_Average"] = blue_career_submission_average
    fvf_df["B_Knockdowns"] = blue_knockdowns

    fvf_df["R_Name"] = red_name
    fvf_df["R_Age"] = red_age
    fvf_df["R_Height"] = red_height
    fvf_df["R_Weight"] = red_weight
    fvf_df["R_Reach"] = red_reach
    fvf_df["R_Stance"] = red_stance
    fvf_df["R_Age_Bucket"] = red_age_bucket
    fvf_df["R_Height_Bucket"] = red_height_bucket
    fvf_df["R_Wins"] = red_wins
    fvf_df["R_Draws"] = red_draws
    fvf_df["R_No_Contest"] = red_no_contest
    fvf_df[
        "R_Career_Significant_Strikes_Landed_PM"
    ] = red_career_significant_strikes_landed_PM
    fvf_df["R_Career_Striking_Accuracy"] = red_career_striking_accuracy
    fvf_df["R_Career_Takedown_Average"] = red_career_submission_average
    fvf_df["R_Career_Takedown_Accuracy"] = red_career_takedown_accuracy
    fvf_df["R_Career_Takedown_Defence"] = red_career_takedown_defence
    fvf_df["R_Career_Submission_Average"] = red_career_submission_average
    fvf_df["R_Knockdowns"] = red_knockdowns

    # Predict fight.
    prediction, pred_proba = predict(fvf_df)

    # Display results of prediction.
    if prediction == "Blue":
        predicted_winner = blue_name.iloc[0]
    elif prediction == "Red":
        predicted_winner = red_name.iloc[0]

    if predicted_winner == blue_name.iloc[0]:
        winner = f'<b>The predicted winner of this fight, from <span style="color:#636EFA;">the blue corner</span>, is: <span style="color:#636EFA;font-size:20px">{predicted_winner}</span></b>'
    elif predicted_winner == red_name.iloc[0]:
        winner = f'<b>The predicted winner of this fight, from <span style="color:#EF563B;">the red corner</span>, is: <span style="color:#EF563B;font-size:20px">{predicted_winner}</span></b>'
    st.markdown(winner, unsafe_allow_html=True)

    # Display probability of prediction.
    st.write(
        f"The predicted probability of the winner being {blue_name.iloc[0]} is: {round(pred_proba[0][0] * 100, 2)}%"
    )
    st.write(
        f"The predicted probability of the winner being {red_name.iloc[0]} is: {round(pred_proba[0][1] * 100, 2)}%"
    )

    # Display statistics of selected fighter.
    blue_header = f'<h1><b><span style="color:#636EFA">Blue</b></h1>'
    red_header = f'<h1><b><span style="color:#EF563B">Red</b></h1>'

    col1, col2 = st.columns(2)
    col1.markdown(blue_header, unsafe_allow_html=True)
    col1.subheader(f"{blue_fighter}")
    col2.markdown(red_header, unsafe_allow_html=True)
    col2.subheader(f"{red_fighter}")

    # Display blue fighter stats
    col1.write(f"Age: {blue_age.iloc[0]}")
    col1.write(f"Height: {blue_height.iloc[0]}")
    col1.write(f"Weight: {blue_weight.iloc[0]}")
    col1.write(f"Reach: {blue_reach.iloc[0]}")
    col1.write(f"Stance: {blue_stance.iloc[0]}")

    # Display red fighter stats
    col2.write(f"Age: {red_age.iloc[0]}")
    col2.write(f"Height: {red_height.iloc[0]}")
    col2.write(f"Weight: {red_weight.iloc[0]}")
    col2.write(f"Reach: {red_reach.iloc[0]}")
    col2.write(f"Stance: {red_stance.iloc[0]}")


elif data_selection == "Create your own fighter":
    st.subheader("Create your own fighter")
    # TODO: Predict fight.
    # TODO: Display probability of prediction.
    # TODO: Display statistics of selected fighter.

# Pie Charts
# ----- #
# `Win Rate By` Charts
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
        legend=dict(title="<b>Age Range:</b> "),
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

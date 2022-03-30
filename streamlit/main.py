import pandas as pd
import streamlit as st

def print_hi():
    df = pd.read_csv("../Resources/clean_scraped_data.csv")
    col_left, col_mid, col_right = st.columns(3)

    with col_left:
        fighter_one_dropbox = st.selectbox(
            "Select Fighter 1",
            ("Test", "Test2",)
        )
        st.write("you selected", fighter_one_dropbox)

    with col_mid:
        st.write("test")

    with col_right:
        fighter_two_dropbox = st.selectbox(
            "Select Fighter 2",
            ("Test2", "Test1",)
        )
        st.write("you selected", fighter_two_dropbox)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

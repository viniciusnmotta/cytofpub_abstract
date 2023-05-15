import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.markdown('<h1 style = "color:Green;">CyTOF publications</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: Blue;">by Vinicius Motta</p>', unsafe_allow_html=True)

st.write(
    """***Publications were retrieved from a pubmed search using "cytof" or "mass cytometry" as keywords***
    """
)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        #if I want return data frame or write data frame
        # return st.dataframe(df.style.format({"PMID":"{:.0f}"}))
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                # _min = float(df[column].min())
                _min = int(df[column].min())
                # _max = float(df[column].max())
                _max = int(df[column].max())
                step = 1 #(_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
    # if I want to display the results as html with hyperlink
    # df["link"] = ['<a target = "_blank" href="{}">link</a>'.format(t) for t in df["link"]]
    # df = df.to_html(escape=False)
    # return st.write(df, unsafe_allow_html=True)
    return df


df = pd.read_csv(
    "publication_abstract_merged.csv"
)
df = df.loc[:,["Year","full_authors","Title","short_citation","Abstract", "Keyword",'link']]
#If I want to display table as html with hyperlink after searching
#  filter_dataframe(df)

st.dataframe(filter_dataframe(df).style.format({"PMID":"{:.0f}"}), height=1000)

import pandas as pd
import streamlit as st
import numpy as np
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st. set_page_config(layout="wide",)

st.markdown('<h1 style = "color:Green;">CyTOF publications</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #DCD427;">by Vinicius Motta</p>', unsafe_allow_html=True)

st.write(
    """***Publications were retrieved from a pubmed search using "cytof" or "mass cytometry" as keywords.***
    """
)

with open ("update.csv", "r") as f:
    update = f.read()

st.markdown('Last update: <b style = "color: #087099; font-size: 1.2REM"><i>{}</i></b>'.format(update), unsafe_allow_html=True)



def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add search boxes to filter data")
    

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
        to_filter_columns = st.multiselect("Choose columns to filter dataframe on", df.columns,default=df.columns[1])
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
                    f"Substring or regex in {column}", placeholder="Type search terms here"
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
).fillna("---")
df = df.loc[:,["Year","full_authors","Title","short_citation","Abstract", "Keyword",'link']]
df["Keyword"] = df["Keyword"].str.replace("Keywords: ","")

#  filter_dataframe(df)
# df2 = filter_dataframe(df).copy()
df2 = df.copy()



# with col2:
#     st.download_button("download table", df2.to_csv(index=False).encode("utf-8"),"pub.csv")
# with col1:
#     st.markdown('<b style = "font-size:1REM; color:tomato;">{}</b> articles'.format(len(df2)), unsafe_allow_html=True)

# st.dataframe(df2.set_index(df2.columns[0]), 
#              column_config = {
#                  "full_authors": st.column_config.TextColumn("Authors", width = "medium", max_chars = 10),
#                  "Title": st.column_config.TextColumn("Title", width = "large"),
#                  "link": st.column_config.LinkColumn("link")
#              },
#              height=400)
# st.markdown("<br>", unsafe_allow_html=True)
text_1, text_2 = st.columns(2)
with text_1:
    st.markdown('''<h6>- Use keywords for each column to search for publications.<br>
                - More than one keyword can be used in each searching box.<br> 
                - For example, use <i><b>Cancer Breast Imaging</i> in the Title box.<br>
                - Don't use words like 'AND' 'OR'.<br>
                - Results are returned based on AND logical operation for all keywords.</h6>''', unsafe_allow_html=True)
    
with text_2:
    st.markdown(
                '''<h6>Tips:<br>
                -Double click each cell to expand and read the full content.<br>
                -Double click cells in the Link column creates a hyperlink. <br>
                -Columns width can be adjusted<br>
                -Click on columns' header to sort cells.</h6>''', unsafe_allow_html=True 
    )
# st.markdown("<br>", unsafe_allow_html=True)


s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
col1, col2,col3 = st.columns([2,2,4])
### test to create a search box for each column
# if I want to do OR operation
# author = df2["full_authors"].apply(lambda x: True if any(i in x for i in author) else False)
# if I want to do like AND use all()
with s_col1:
    author = st.text_input("Author", "").split()
    author = df2["full_authors"].str.lower().apply(lambda x: True if all(i.lower() in x for i in author) else False)

with s_col2:
    title = st.text_input("Title", "").split()
    title = df2["Title"].str.lower().apply(lambda x: True if all(i.lower() in x for i in title) else False)

with s_col3:
    abstract = st.text_input("Abstract", "").split()
    abstract = df2["Abstract"].str.lower().apply(lambda x: True if all(i.lower() in x for i in abstract) else False)

with s_col4:
    citation = st.text_input("Citation", "").split()
    citation = df2["short_citation"].str.lower().apply(lambda x: True if all(i.lower() in x for i in citation) else False)

with s_col5:
    keyword = st.text_input("Keyword", "").split()
    keyword = df2["Keyword"].str.lower().apply(lambda x: True if all(i.lower() in x for i in keyword) else False)

# st.markdown("<br>", unsafe_allow_html=True)
sel = author & title & abstract & citation & keyword
st.dataframe(df2[sel],
                column_config={
                    "full_authors": st.column_config.TextColumn("Authors", width="medium"),
                    "link": st.column_config.LinkColumn("Link"),
                    "Year": st.column_config.NumberColumn("Year", format="%d"),
                    # "short_citation": st.column_config.TextColumn("Citation", width="small"),
                    "Abstract": st.column_config.TextColumn("Abstract", width="medium"),
                    "Title": st.column_config.TextColumn('Title', width="large"),
                    "Keyword": st.column_config.TextColumn("Keywords", width="small")
                }, 
                column_order=("Year", "full_authors", "Title", "Abstract", "short_citation","Keyword", "link"),
                hide_index=True
                )

with col1:
    st.markdown('<b style = "font-size:1REM; color:tomato;">{}</b> articles'.format(len(df2[sel])), unsafe_allow_html=True)
with col2:
    st.download_button("download table", df2[sel].to_csv(index=False).encode("utf-8"),"pub.csv")

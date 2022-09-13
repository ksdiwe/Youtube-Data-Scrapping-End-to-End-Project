import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

plt.style.use('dark_background')


@st.cache

def load_data():
    df_channel = pd.read_csv('channalStats.csv')
    df_KN = pd.read_csv('Updated_KrishNaik.csv')
    df_HC = pd.read_csv('Updated_hitesh.csv')
    df_T = pd.read_csv('Updated_telusko.csv')
    df_S = pd.read_csv('Updated_MysirG.csv')
    return df_channel, df_KN, df_HC, df_T, df_S


df_channel, df_KN, df_HC, df_T, df_S = load_data()


numeric_col_k = df_KN.select_dtypes(['float64', 'float32', 'int32', 'int64']).columns
numeric_col_h = df_HC.select_dtypes(['float64', 'float32', 'int32', 'int64']).columns
numeric_col_t = df_T.select_dtypes(['float64', 'float32', 'int32', 'int64']).columns
numeric_col_g = df_S.select_dtypes(['float64', 'float32', 'int32', 'int64']).columns


# Define Functions


def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try:
        return props if v < 0 else None
    except:
        pass


def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try:
        return props if v > 0 else None
    except:
        pass


add_sidebar = st.sidebar.selectbox('Youtuber', ('Home Page', 'Krish Naik',
                                                'Hitesh Choudhary', 'Naveen Reddy', 'Saurabh Shukla'))

if add_sidebar == 'Krish Naik':
    st.header("Krish Naiks's Youtube Stats")
    url = df_channel['thumbnail'][0]
    st.image(url, width=400, caption='Krish Naik')
    des = df_channel['description'][0]
    st.write(des)

    checkbox = st.sidebar.checkbox("Show Data")
    if checkbox:
        st.dataframe(data=df_KN)

    # create scatter plot
    st.sidebar.subheader("Scatter Plot Setup")
    fig, ax = plt.subplots()
    select_box1 = st.sidebar.selectbox(label='X axis', options=numeric_col_k)
    select_box2 = st.sidebar.selectbox(label="Y axis", options=numeric_col_k)

    plt.scatter(x=select_box1, y=select_box2, data=df_KN, color='#f21111', alpha=0.5)
    st.pyplot(fig)

if add_sidebar == 'Home Page':
    st.title("Top Youtubers Comparison")
    st.subheader("Comparison on the basis of Subscribers")
    st.bar_chart(data=df_channel.sort_values('subscribers', ascending=False), x='channelName', y='subscribers')

    st.subheader("Comparison on the basis of Views")
    st.bar_chart(x='channelName', y='views', data=df_channel.sort_values('views', ascending=False))

if add_sidebar == 'Hitesh Choudhary':
    st.header("Hitesh Choudhary's Youtube Stats")
    url = df_channel['thumbnail'][1]
    st.image(url, width=400, caption='Hitesh Choudhary')
    des1 = df_channel['description'][1]
    st.write(des1)

    checkbox = st.sidebar.checkbox("Show Data")
    if checkbox:
        st.dataframe(data=df_HC)

    # create scatter plot
    st.sidebar.subheader("Scatter Plot Setup")
    fig, ax = plt.subplots()
    select_box1 = st.sidebar.selectbox(label='X axis', options=numeric_col_h)
    select_box2 = st.sidebar.selectbox(label="Y axis", options=numeric_col_h)

    plt.scatter(x=select_box1, y=select_box2, data=df_HC, color='#f21111', alpha=0.5)
    st.pyplot(fig)

if add_sidebar == 'Naveen Reddy':
    st.header("Telusko's Youtube Stats")
    url = df_channel['thumbnail'][3]
    st.image(url, width=400, caption='Telusko')
    des2 = df_channel['description'][3]
    st.write(des2)

    checkbox = st.sidebar.checkbox("Show Data")
    if checkbox:
        st.dataframe(data=df_T)

    # create scatter plot
    st.sidebar.subheader("Scatter Plot Setup")
    fig, ax = plt.subplots()
    select_box1 = st.sidebar.selectbox(label='X axis', options=numeric_col_t)
    select_box2 = st.sidebar.selectbox(label="Y axis", options=numeric_col_t)

    plt.scatter(x=select_box1, y=select_box2, data=df_T, color='#f21111', alpha=0.5)
    st.pyplot(fig)

if add_sidebar == 'Saurabh Shukla':
    st.header("MySirG.com's Youtube Stats")
    url = df_channel['thumbnail'][2]
    st.image(url, width=400, caption='Saurabh Shukla')
    desg = df_channel['description'][2]
    st.write(desg)

    checkbox = st.sidebar.checkbox("Show Data")
    if checkbox:
        st.dataframe(data=df_S)

    # create scatter plot
    st.sidebar.subheader("Scatter Plot Setup")
    fig, ax = plt.subplots()
    select_box1 = st.sidebar.selectbox(label='X axis', options=numeric_col_g)
    select_box2 = st.sidebar.selectbox(label="Y axis", options=numeric_col_g)

    plt.scatter(x=select_box1, y=select_box2, data=df_S, color='#f21111', alpha=0.5)
    st.pyplot(fig)

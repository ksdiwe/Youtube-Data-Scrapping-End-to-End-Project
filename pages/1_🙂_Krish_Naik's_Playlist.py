import pandas as pd
import streamlit as st
import numpy as np
import datetime as dt
from datetime import date
import plotly.graph_objects as go


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


def load_data():
    df_krish = pd.read_csv('Updated_KrishNaik.csv').iloc[1:, :]
    return df_krish


# create dataframes from the function
df_krish = load_data()

# additional data engineering for aggregated data
df_krish_diff = df_krish.copy()
df_krish_diff['Video publish time'] = pd.to_datetime(df_krish_diff['Video publish time'])
metric_date_12mo = df_krish_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_agg = df_krish_diff[df_krish_diff['Video publish time'] >= metric_date_12mo].median()

# create differences from the median for values
# Just numeric columns
numeric_cols = np.array((df_krish_diff.dtypes == 'float64') | (df_krish_diff.dtypes == 'int64'))
df_krish_diff.iloc[:, numeric_cols] = (df_krish_diff.iloc[:, numeric_cols] - median_agg).div(median_agg)

# merge daily data with publish data to get delta
today = date.today()
df_krish_diff['date'] = today.strftime("%Y-%m-%d")
df_krish_diff['date'] = pd.to_datetime(df_krish_diff.date)
df_krish_diff['days_published'] = (df_krish_diff['date'] - df_krish_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data
df_krish['Video publish time'] = pd.to_datetime(df_krish['Video publish time'])
date_12mo = df_krish['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yrk = df_krish_diff[df_krish_diff['Video publish time'] >= date_12mo]


def percentile_80(g):
    return np.percentile(g, 80)


def percentile_20(g):
    return np.percentile(g, 20)


# get daily view data (first 30), median & percentiles
views_days_k = pd.pivot_table(df_time_diff_yrk, values='viewCount', index='days_published',
                              aggfunc=[np.mean, np.median, percentile_80, percentile_20]).reset_index()
views_days_k.columns = ['days_published', 'mean_views', 'median_views', '80pct_views', '20pct_views']
views_days_k = views_days_k[views_days_k['days_published'].between(0, 30)]
views_cumulative_k = views_days_k.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulative_k.loc[:, ['median_views', '80pct_views', '20pct_views']] = views_cumulative_k.loc[:,
                                                                            ['median_views', '80pct_views', '20pct_views']].cumsum()

#######################################################################
videos1 = tuple(df_krish['title'])
st.write("Krish Naik's Playlist")
video_select1 = st.selectbox("Pick a Video:", videos1)

df_vdo = df_krish[df_krish['title'] == video_select1]['video_id'].values[0]
link = ("https://youtu.be/" + str(df_vdo))
st.video(link)

#######################################################################
df_krish_metrics = df_krish[df_krish['title'] == video_select1][
    ['viewCount', 'likeCount', 'commentCount', 'Video publish time',
     'Avg_duration_sec']]
metric_date_6mok = df_krish_metrics['Video publish time'].max() - pd.DateOffset(months=6)
metric_date_12mok = df_krish_metrics['Video publish time'].max() - pd.DateOffset(months=12)
metric_medians6mok = df_krish_metrics[df_krish_metrics['Video publish time'] >= metric_date_6mok].median()
metric_medians12mok = df_krish_metrics[df_krish_metrics['Video publish time'] >= metric_date_12mok].median()

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

count = 0
for i in metric_medians6mok.index:
    with columns[count]:
        delta = (metric_medians6mok[i] - metric_medians12mok[i]) / metric_medians12mok[i]
        st.metric(label=i, value=round(metric_medians6mok[i], 1), delta="{:.2%}".format(delta))
        count += 1
        if count >= 5:
            count = 0

######################################################################
agg_time_filteredk = df_krish_diff[df_krish_diff['title'] == video_select1]
firstk_30 = agg_time_filteredk[agg_time_filteredk['days_published'].between(0, 30)]
firstk_30 = firstk_30.sort_values('days_published')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=views_cumulative_k['days_published'], y=views_cumulative_k['20pct_views'],
                          mode='lines',
                          name='20th percentile', line=dict(color='purple', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulative_k['days_published'], y=views_cumulative_k['median_views'],
                          mode='lines',
                          name='50th percentile', line=dict(color='black', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulative_k['days_published'], y=views_cumulative_k['80pct_views'],
                          mode='lines',
                          name='80th percentile', line=dict(color='royalblue', dash='dash')))
fig2.add_trace(go.Scatter(x=firstk_30['days_published'], y=firstk_30['viewCount'].cumsum(),
                          mode='lines',
                          name='Current Video', line=dict(color='firebrick', width=8)))

fig2.update_layout(title='View comparison first 30 days',
                   xaxis_title='Days Since Published',
                   yaxis_title='Cumulative views')

st.plotly_chart(fig2)

########################################################################################################################
df_kdes = df_krish[df_krish['title'] == video_select1]['description'].values[0]
st.subheader('Description:')
st.write(df_kdes)

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
    df_hitesh = pd.read_csv('Updated_hitesh.csv').iloc[1:, :]
    return df_hitesh


# create dataframes from the function
df_hitesh = load_data()

# additional data engineering for aggregated data
df_hitesh_diff = df_hitesh.copy()
df_hitesh_diff['Video publish time'] = pd.to_datetime(df_hitesh_diff['Video publish time'])
metric_date_12mo = df_hitesh_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_agg = df_hitesh_diff[df_hitesh_diff['Video publish time'] >= metric_date_12mo].median()

# create differences from the median for values
# Just numeric columns
numeric_cols = np.array((df_hitesh_diff.dtypes == 'float64') | (df_hitesh_diff.dtypes == 'int64'))
df_hitesh_diff.iloc[:, numeric_cols] = (df_hitesh_diff.iloc[:, numeric_cols] - median_agg).div(median_agg)

# merge daily data with publish data to get delta
today = date.today()
df_hitesh_diff['date'] = today.strftime("%Y-%m-%d")
df_hitesh_diff['date'] = pd.to_datetime(df_hitesh_diff.date)
df_hitesh_diff['days_published'] = (df_hitesh_diff['date'] - df_hitesh_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data
df_hitesh['Video publish time'] = pd.to_datetime(df_hitesh['Video publish time'])
date_12mo = df_hitesh['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yr = df_hitesh_diff[df_hitesh_diff['Video publish time'] >= date_12mo]


def percentile_80(g):
    return np.percentile(g, 80)


def percentile_20(g):
    return np.percentile(g, 20)


# get daily view data (first 30), median & percentiles
views_days = pd.pivot_table(df_time_diff_yr, values='viewCount', index='days_published',
                            aggfunc=[np.mean, np.median, percentile_80, percentile_20]).reset_index()
views_days.columns = ['days_published', 'mean_views', 'median_views', '80pct_views', '20pct_views']
views_days = views_days[views_days['days_published'].between(0, 30)]
views_cumulative = views_days.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']] = views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']].cumsum()

#######################################################################
videos2 = tuple(df_hitesh['title'])
st.write("Hitesh Choudhary's Playlist")
video_select2 = st.selectbox("Pick a Video:", videos2)

df_vdo2 = df_hitesh[df_hitesh['title'] == video_select2]['video_id'].values[0]
link2 = ("https://youtu.be/" + str(df_vdo2))
st.video(link2)

#######################################################################
df_hitesh_metrics = df_hitesh[df_hitesh['title'] == video_select2][['viewCount', 'likeCount', 'commentCount', 'Video publish time', 'Avg_duration_sec']]
metric_date_6mo = df_hitesh_metrics['Video publish time'].max() - pd.DateOffset(months=6)
metric_date_12mo = df_hitesh_metrics['Video publish time'].max() - pd.DateOffset(months=12)
metric_medians6mo = df_hitesh_metrics[df_hitesh_metrics['Video publish time'] >= metric_date_6mo].median()
metric_medians12mo = df_hitesh_metrics[df_hitesh_metrics['Video publish time'] >= metric_date_12mo].median()

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

count = 0
for i in metric_medians6mo.index:
    with columns[count]:
        delta = (metric_medians6mo[i] - metric_medians12mo[i]) / metric_medians12mo[i]
        st.metric(label=i, value=round(metric_medians6mo[i], 1), delta="{:.2%}".format(delta))
        count += 1
        if count >= 5:
            count = 0

######################################################################
agg_time_filtered = df_hitesh_diff[df_hitesh_diff['title'] == video_select2]
first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0, 30)]
first_30 = first_30.sort_values('days_published')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                              mode='lines',
                              name='20th percentile', line=dict(color='purple', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                              mode='lines',
                              name='50th percentile', line=dict(color='black', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                              mode='lines',
                              name='80th percentile', line=dict(color='royalblue', dash='dash')))
fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['viewCount'].cumsum(),
                              mode='lines',
                              name='Current Video', line=dict(color='firebrick', width=8)))

fig2.update_layout(title='View comparison first 30 days',
                       xaxis_title='Days Since Published', yaxis_title='Cumulative views')

st.plotly_chart(fig2)

########################################################################################################################
df_des = df_hitesh[df_hitesh['title'] == video_select2]['description'].values[0]
st.subheader('Description:')
st.write(df_des)

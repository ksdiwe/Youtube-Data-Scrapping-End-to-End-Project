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
    df_mysirG = pd.read_csv('Updated_MysirG.csv').iloc[1:, :]
    return df_mysirG


# create dataframes from the function
df_mysirG = load_data()


# additional data engineering for aggregated data
df_mysirG_diff = df_mysirG.copy()
df_mysirG_diff['Video publish time'] = pd.to_datetime(df_mysirG_diff['Video publish time'])
metric_date_12mog = df_mysirG_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_aggg = df_mysirG_diff[df_mysirG_diff['Video publish time'] >= metric_date_12mog].median()

# create differences from the median for values
# Just numeric columns
numeric_colsg = np.array((df_mysirG_diff.dtypes == 'float64') | (df_mysirG_diff.dtypes == 'int64'))
df_mysirG_diff.iloc[:, numeric_colsg] = (df_mysirG_diff.iloc[:, numeric_colsg] - median_aggg).div(median_aggg)

# merge daily data with publish data to get delta
today = date.today()
df_mysirG_diff['date'] = today.strftime("%Y-%m-%d")
df_mysirG_diff['date'] = pd.to_datetime(df_mysirG_diff.date)
df_mysirG_diff['days_published'] = (df_mysirG_diff['date'] - df_mysirG_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data
df_mysirG['Video publish time'] = pd.to_datetime(df_mysirG['Video publish time'])
date_12mog = df_mysirG['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yrg = df_mysirG_diff[df_mysirG_diff['Video publish time'] >= date_12mog]


def percentile_80(g):
    return np.percentile(g, 80)


def percentile_20(g):
    return np.percentile(g, 20)


# get daily view data (first 30), median & percentiles
views_daysg = pd.pivot_table(df_time_diff_yrg, values='viewCount', index='days_published',
                            aggfunc=[np.mean, np.median, percentile_80, percentile_20]).reset_index()
views_daysg.columns = ['days_published', 'mean_views', 'median_views', '80pct_views', '20pct_views']
views_daysg = views_daysg[views_daysg['days_published'].between(0, 30)]
views_cumulativeg = views_daysg.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulativeg.loc[:, ['median_views', '80pct_views', '20pct_views']] = views_cumulativeg.loc[:, ['median_views', '80pct_views', '20pct_views']].cumsum()

#######################################################################
videos4 = tuple(df_mysirG['title'])
st.write("MySirG.com's Playlist")
video_select4 = st.selectbox("Pick a Video:", videos4)

df_vdo4 = df_mysirG[df_mysirG['title'] == video_select4]['video_id'].values[0]
link4 = ("https://youtu.be/" + str(df_vdo4))
st.video(link4)

#######################################################################
df_mysirG_metrics = df_mysirG[df_mysirG['title'] == video_select4][['viewCount', 'likeCount', 'commentCount', 'Video publish time', 'Avg_duration_sec']]
metric_date_6mog = df_mysirG_metrics['Video publish time'].max() - pd.DateOffset(months=6)
metric_date_12mog = df_mysirG_metrics['Video publish time'].max() - pd.DateOffset(months=12)
metric_medians6mog = df_mysirG_metrics[df_mysirG_metrics['Video publish time'] >= metric_date_6mog].median()
metric_medians12mog = df_mysirG_metrics[df_mysirG_metrics['Video publish time'] >= metric_date_12mog].median()

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

count = 0
for i in metric_medians6mog.index:
    with columns[count]:
        delta = (metric_medians6mog[i] - metric_medians12mog[i]) / metric_medians12mog[i]
        st.metric(label=i, value=round(metric_medians6mog[i], 1), delta="{:.2%}".format(delta))
        count += 1
        if count >= 5:
            count = 0

######################################################################
agg_time_filteredg = df_mysirG_diff[df_mysirG_diff['title'] == video_select4]
first_30g = agg_time_filteredg[agg_time_filteredg['days_published'].between(0, 30)]
first_30g = first_30g.sort_values('days_published')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=views_cumulativeg['days_published'], y=views_cumulativeg['20pct_views'],
                              mode='lines',
                              name='20th percentile', line=dict(color='purple', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulativeg['days_published'], y=views_cumulativeg['median_views'],
                              mode='lines',
                              name='50th percentile', line=dict(color='black', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulativeg['days_published'], y=views_cumulativeg['80pct_views'],
                              mode='lines',
                              name='80th percentile', line=dict(color='royalblue', dash='dash')))
fig2.add_trace(go.Scatter(x=first_30g['days_published'], y=first_30g['viewCount'].cumsum(),
                              mode='lines',
                              name='Current Video', line=dict(color='firebrick', width=8)))

fig2.update_layout(title='View comparison first 30 days',
                       xaxis_title='Days Since Published',
                       yaxis_title='Cumulative views')

st.plotly_chart(fig2)

########################################################################################################################
df_desg = df_mysirG[df_mysirG['title'] == video_select4]['description'].values[0]
st.subheader('Description:')
st.write(df_desg)

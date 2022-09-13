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
    df_telusko = pd.read_csv('Updated_telusko.csv').iloc[1:, :]
    return df_telusko


# create dataframes from the function
df_telusko = load_data()


# additional data engineering for aggregated data
df_telusko_diff = df_telusko.copy()
df_telusko_diff['Video publish time'] = pd.to_datetime(df_telusko_diff['Video publish time'])
metric_date_12mot = df_telusko_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_aggt = df_telusko_diff[df_telusko_diff['Video publish time'] >= metric_date_12mot].median()

# create differences from the median for values
# Just numeric columns
numeric_colst = np.array((df_telusko_diff.dtypes == 'float64') | (df_telusko_diff.dtypes == 'int64'))
df_telusko_diff.iloc[:, numeric_colst] = (df_telusko_diff.iloc[:, numeric_colst] - median_aggt).div(median_aggt)

# merge daily data with publish data to get delta
today = date.today()
df_telusko_diff['date'] = today.strftime("%Y-%m-%d")
df_telusko_diff['date'] = pd.to_datetime(df_telusko_diff.date)
df_telusko_diff['days_published'] = (df_telusko_diff['date'] - df_telusko_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data
df_telusko['Video publish time'] = pd.to_datetime(df_telusko['Video publish time'])
date_12mot = df_telusko['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yrt = df_telusko_diff[df_telusko_diff['Video publish time'] >= date_12mot]


def percentile_80(g):
    return np.percentile(g, 80)


def percentile_20(g):
    return np.percentile(g, 20)


# get daily view data (first 30), median & percentiles
views_dayst = pd.pivot_table(df_time_diff_yrt, values='viewCount', index='days_published',
                            aggfunc=[np.mean, np.median, percentile_80, percentile_20]).reset_index()
views_dayst.columns = ['days_published', 'mean_views', 'median_views', '80pct_views', '20pct_views']
views_dayst = views_dayst[views_dayst['days_published'].between(0, 30)]
views_cumulativet = views_dayst.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulativet.loc[:, ['median_views', '80pct_views', '20pct_views']] = views_cumulativet.loc[:, ['median_views', '80pct_views', '20pct_views']].cumsum()

#######################################################################
videos3 = tuple(df_telusko['title'])
st.write("Telusko's Playlist")
video_select3 = st.selectbox("Pick a Video:", videos3)

df_vdo3 = df_telusko[df_telusko['title'] == video_select3]['video_id'].values[0]
link3 = ("https://youtu.be/" + str(df_vdo3))
st.video(link3)

#######################################################################
df_telusko_metrics = df_telusko[df_telusko['title'] == video_select3][['viewCount', 'likeCount', 'commentCount', 'Video publish time', 'Avg_duration_sec']]
metric_date_6mot = df_telusko_metrics['Video publish time'].max() - pd.DateOffset(months=6)
metric_date_12mot = df_telusko_metrics['Video publish time'].max() - pd.DateOffset(months=12)
metric_medians6mot = df_telusko_metrics[df_telusko_metrics['Video publish time'] >= metric_date_6mot].median()
metric_medians12mot = df_telusko_metrics[df_telusko_metrics['Video publish time'] >= metric_date_12mot].median()

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

count = 0
for i in metric_medians6mot.index:
    with columns[count]:
        delta = (metric_medians6mot[i] - metric_medians12mot[i]) / metric_medians12mot[i]
        st.metric(label=i, value=round(metric_medians6mot[i], 1), delta="{:.2%}".format(delta))
        count += 1
        if count >= 5:
            count = 0

######################################################################
agg_time_filteredt = df_telusko_diff[df_telusko_diff['title'] == video_select3]
first_30t = agg_time_filteredt[agg_time_filteredt['days_published'].between(0, 30)]
first_30t = first_30t.sort_values('days_published')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=views_cumulativet['days_published'], y=views_cumulativet['20pct_views'],
                              mode='lines',
                              name='20th percentile', line=dict(color='purple', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulativet['days_published'], y=views_cumulativet['median_views'],
                              mode='lines',
                              name='50th percentile', line=dict(color='black', dash='dash')))
fig2.add_trace(go.Scatter(x=views_cumulativet['days_published'], y=views_cumulativet['80pct_views'],
                              mode='lines',
                              name='80th percentile', line=dict(color='royalblue', dash='dash')))
fig2.add_trace(go.Scatter(x=first_30t['days_published'], y=first_30t['viewCount'].cumsum(),
                              mode='lines',
                              name='Current Video', line=dict(color='firebrick', width=8)))

fig2.update_layout(title='View comparison first 30 days',
                       xaxis_title='Days Since Published',
                       yaxis_title='Cumulative views')

st.plotly_chart(fig2)

########################################################################################################################
df_dest = df_telusko[df_telusko['title'] == video_select3]['description'].values[0]
st.subheader('Description:')
st.write(df_dest)

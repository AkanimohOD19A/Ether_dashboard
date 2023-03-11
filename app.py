import pandas as pd
import streamlit as st
from scipy import stats
from datetime import datetime, date
from retrieve_ens import get_data, get_subgraphs
import plotly.figure_factory as ff
import numpy as np
import os


@st.cache_data(persist="disk")
def clean_store_data():
    data_path = './daily_ens-data/'
    today_date = str(date.today())

    filepath = data_path + today_date + '.csv'
    ens_df = get_subgraphs()
    ## Cleaning
    ens_df = ens_df.drop(columns=['owner_address'])
    ens_df["expiry_date"] = pd.to_datetime(ens_df["expiry_date"])
    ens_df["registration_date"] = pd.to_datetime(ens_df["registration_date"])
    ens_df['registration_hour'] = ens_df['registration_date'].dt.hour
    ens_df['st_registration_cost_ether'] = stats.zscore(ens_df['registration_cost_ether'])

    ens_df.to_csv(filepath, index=False)

    print(f'Saved data to {filepath}')
    return ens_df


curr_df = clean_store_data()
# curr_df = pd.read_csv('./daily_ens-data/2023-03-10.csv')
curr_time = datetime.now()
### function that manages for date times
#### Comes here

## Build Dashboard

st.title("Competition Entry: Dashboard of ENS dataset")
st.write("Blockchain is a technology that allows transactions and data "
         "to be recorded and verified without a central authority. "
         "Here we get to use the first 1000 records on a daily basis from the graphprotocol"
         "to create distribution and dashboard")

## -> Sidebar Properties
st.sidebar.info('Computes a daily entry of ENS data and plots a real time telemetry based on your own entry ✨ ✨')
st.sidebar.write(curr_time.hour, ':', curr_time.minute, ':', curr_time.second)

minimum_hr = min(curr_df['registration_hour'])
maximum_hr = max(curr_df['registration_hour'])

if st.sidebar.selectbox("Filter to certain Periods", ("No", "Yes")) == "Yes":
    values = st.sidebar.slider(
        'Select a range of values',
        minimum_hr, maximum_hr, (0, 1), step=1)
    st.write('You have selected hours:', values)
    line_chart_df = curr_df[['registration_hour', 'registration_cost_ether', 'st_registration_cost_ether']]
    line_chart_df = line_chart_df[
        (line_chart_df['registration_hour'] == values[0]) | (line_chart_df['registration_hour'] == values[1])]
else:
    line_chart_df = curr_df[['registration_hour', 'registration_cost_ether', 'st_registration_cost_ether']]

max_rce = max(curr_df['registration_cost_ether'])
min_rce = min(curr_df['registration_cost_ether'])

st.sidebar.markdown("""---""")
st.sidebar.markdown(f"### Highest Registration: {round(max_rce, 2)} ETH")
if st.sidebar.button("View Max Distribution"):
    max_rce_df = curr_df[curr_df['registration_cost_ether'] == max_rce]
    st.sidebar.dataframe(max_rce_df.T.style.highlight_max(axis=1))

st.sidebar.markdown(f"### Lowest Registration: {round(min_rce, 2)} ETH")
if st.sidebar.button("View Min Distribution"):
    min_rce_df = curr_df[curr_df['registration_cost_ether'] == min_rce]
    st.sidebar.dataframe(min_rce_df.T.style.highlight_max(axis=1))

st.sidebar.info("Made with ❤ by the AfroLogicInsect")
st.markdown('##')  ##-> Empty Space Divider

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        '###### Line chart of the distribution of selected time bound of ether scores against registration hour.')
    st.line_chart(data=line_chart_df,
                  x='registration_hour',
                  y=['registration_cost_ether', 'st_registration_cost_ether'],
                  use_container_width=True, height=400)
with col2:
    st.markdown('###### Dataframe showing the distribution of selected time bound of ether scores.')
    st.dataframe(line_chart_df.style.highlight_max(axis=0),
                 use_container_width=True, height=400)

# st.markdown('##')  ##-> Empty Space Divider
# hist_data = [line_chart_df['registration_cost_ether'], line_chart_df['st_registration_cost_ether']]
# group_labels = ['Ether', 'Standardized_Ether']
#
# fig = ff.create_distplot(
#     hist_data, group_labels, bin_size=[.1, .25, .5]
# )
# st.plotly_chart(fig, use_container_width=True)

st.markdown('##')  ##-> Empty Space Divider
# file_path = "daily_ens-data/"
# filenames = os.listdir(file_path)
# data_file = st.selectbox('Select a file', filenames)
# ref_data = pd.read_csv(os.path.join(file_path, data_file), 'r').read()
st.write("A blockchain is a distributed database or ledger that is shared "
         "among the nodes of a computer network. As a database, a blockchain stores "
         "information electronically in digital format."
         "The innovation with a blockchain is that it guarantees the fidelity and security "
         "of a record of data and generates trust without the need for a trusted third party.")

st.markdown('##')  ##-> Empty Space Divider

area_data = line_chart_df[['registration_cost_ether', 'st_registration_cost_ether']]
st.area_chart(area_data)

st.markdown('##')  ##-> Empty Space Divider
st.markdown('##')  ##-> Empty Space Divider
st.markdown('##')  ##-> Empty Space Divider

st.write("Disclaimer: Author's knowledge of Blockchain is limited")
st.write("Credits: how to query data from The @graphprotocol by Tony Kipkemboi")

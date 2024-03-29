
from math import ceil
from functools import reduce
from operator import add
import json

import numpy as np
import pandas as pd
import streamlit as st
import requests
from matplotlib import pyplot as plt


def randomy_assign_groups(nbdata, nbmembers_pergroup):
    nbgroups = ceil(nbdata / nbmembers_pergroup)
    if nbdata % nbmembers_pergroup == 0:
        nbgroups_onelessmeber = 0
    else:
        nbgroups_onelessmeber = nbmembers_pergroup - nbdata % nbmembers_pergroup
    labels_to_assign = reduce(
        add,
        [
            [i+1]*(nbmembers_pergroup if i < nbgroups - nbgroups_onelessmeber else nbmembers_pergroup-1)
            for i in range(nbgroups)
        ]
    )
    assignments = np.random.choice(labels_to_assign, replace=False, size=nbdata)
    return assignments


def generate_excel_file(df):
    api_url = "https://pdihs60tm3.execute-api.us-east-1.amazonaws.com/default/excel_generator_lambda"
    payload = json.dumps({
        "dataframe": df.to_dict(orient='list')
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", api_url, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    return response_dict


# Headers
st.set_page_config(page_title='Mouse Group Assignment')
st.header('Group Assignment')

selected_page = st.sidebar.selectbox("Select a page", ['Self-input Parameters', 'Upload File'])

if selected_page == 'Self-input Parameters':
    # Input
    nbdata = st.number_input('Number of data', min_value=2, value=100, step=1)
    nbmembers_pergroup = st.number_input('Number of data in one group', min_value=1, max_value=nbdata, value=5, step=1)

    if st.button('Assign!'):
        df = pd.DataFrame({
            'ID': range(nbdata),
            'groups': randomy_assign_groups(nbdata, nbmembers_pergroup)
        })
        df = df.sort_values(['groups', 'ID'], ascending=True)
        response_dict = generate_excel_file(df)
        url = response_dict['url']
        st.markdown('[Download Excel]({})'.format(url))
        st.dataframe(df)

elif selected_page == 'Upload File':
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        idcolname = df.columns[0]
        valcolname = df.columns[1]
        nbdata = len(df)
        st.markdown('Number of data points: {}'.format(nbdata))
        nbmembers_pergroup = st.number_input(
            'Number of data in one group',
            min_value=1,
            max_value=nbdata,
            value=5,
            step=1
        )
        if st.button('Assign!'):
            assignments = randomy_assign_groups(nbdata, nbmembers_pergroup)
            df['group'] = assignments
            response_dict = generate_excel_file(df)
            url = response_dict['url']
            st.markdown('[Download Excel]({})'.format(url))
            st.dataframe(df)

            fig, ax = plt.subplots()
            ax.scatter(df['group'], df[valcolname])
            ax.set_xlabel('group')
            ax.set_ylabel(valcolname)
            ax.set_xticks(sorted(set(assignments)))
            st.pyplot(fig)
else:
    pass
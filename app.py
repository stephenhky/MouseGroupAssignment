
from math import ceil
from functools import reduce
from operator import add
import json

import numpy as np
import pandas as pd
import streamlit as st
import requests


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


# Headers
st.header('Group Assignment')

# Input
nbdata = st.number_input('Number of data', min_value=2, value=100, step=1)
nbmembers_pergroup = st.number_input('Number of data in one group', min_value=1, max_value=nbdata, value=5, step=1)

if st.button('Assign!'):
    df = pd.DataFrame({
        'ID': range(nbdata),
        'groups': randomy_assign_groups(nbdata, nbmembers_pergroup)
    })
    df = df.sort_values(['groups', 'ID'], ascending=True)

    api_url = "https://pdihs60tm3.execute-api.us-east-1.amazonaws.com/default/excel_generator_lambda"
    payload = json.dumps({
        "dataframe": df.to_dict(orient='list')
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", api_url, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    print(response.text)
    url = response_dict['url']
    st.markdown('[Download Excel]({})'.format(url))
    st.dataframe(df)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import os

import json
import requests
import pyjsonviewer

from functools import reduce
import operator

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

# Using api form LastFm website, to get the most played music genre in the digital platforms. 
# LastFm gets this info through a feature in their app called scrobbling.

API_KEY = os.getenv("API_key")
USER_AGENT = 'Dataquest'

# create a dictionary for our headers and parameters, and make our first request

headers = {
    'user-agent': USER_AGENT
}

payload = {
    'api_key': API_KEY,
    'method': 'chart.gettopartists',
    'format': 'json'
}

r = requests.get('https://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
r.status_code

# APi call function
def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

def my_json(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

my_json(r.json())


# import time to limit the number of times per second that we hit a particular API.

import requests_cache

requests_cache.install_cache()
import time
from IPython.core.display import clear_output

responses = []

page = 1
total_pages = 100 # this is just a dummy number so the loop starts

while page <= total_pages:
    payload = {
        'method': 'chart.gettopartists',
        'limit': 500,
        'page': page
    }

    # print some output so we can see the status
    print("Requesting page {}/{}".format(page, total_pages))
    # clear the output to make things neater
    clear_output(wait = True)

    # make the API call
    response = lastfm_get(payload)

    # if we get an error, print the response and halt the loop
    if response.status_code != 200:
        print(response.text)
        break

    # extract pagination info
    page = int(response.json()['artists']['@attr']['page'])
    total_pages = int(response.json()['artists']['@attr']['totalPages'])

    # append response
    responses.append(response)

    # if it's not a cached result, sleep
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)

    # increment the page number
    page += 1

#we convert our first json response into pandas df to look at the data
res = responses[0]
res_json = res.json()
res_artists = res_json['artists']['artist']
res_df = pd.DataFrame(res_artists)
res_df.head()


#we got a frame for each page we got from the API call
#now we need to concatenate them
frames = [pd.DataFrame(r.json()['artists']['artist']) for r in responses]
artists = pd.concat(frames)
artists.head()

#dropping irrelevant columns
artists.drop(['mbid', 'url', 'image','streamable'], axis = 1, inplace = True) 

#now  we get the genre for each artist we got in last API call 
def lookup_tags(artist):
    response = lastfm_get({
        'method': 'artist.getTopTags',
        'artist':  artist
    })

    # if there's an error, just return nothing
    if response.status_code != 200:
        return None

    # extract the top three tags and turn them into a string
    tags = [t['name'] for t in response.json()['toptags']['tag'][:3]]
    tags_str = ', '.join(tags)

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return tags_str

#to monitor the progress
from tqdm import tqdm
tqdm.pandas()

#we save the top  1000 row in the dataframe, otherwose it's going to be too big
artist_df = artists[:1000]

#saving DF into csv to avoid the api call again when we restart
artist_df.to_csv("./Data/artist_df.csv", index = False)

# Get unique rows in the tags column
new_list = []
for element in artist_df.tags.unique():
    new_list.append(element.split(","))
    
# Flatten the list os lists & make it unique
new_flattened_list = [x.strip().lower().replace(" ", "-") for i in new_list for x in i]
len(new_flattened_list)

freq = {} # stores the frequency of elements
counting = [freq.update({x: new_flattened_list.count(x)}) for x in new_flattened_list]
sort_by_value = dict(sorted(freq.items(), key=lambda item: item[1]))
sort_by_value

df = pd.DataFrame.from_dict(sort_by_value, orient='index')
df

#check the frequency of each genre
df.index = df.index.rename('genre')
df.sort_values(by='frequency',ascending=False, inplace = True)
df.drop(['seen-live'], axis=0, inplace =True)

#we save only the top10
top_genre = df[:10]

top_genre.to_csv("./Data/csv/top_genre.csv", index = True)
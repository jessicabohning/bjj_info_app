# This file will get the subtitle files for Gracie 2.0 Side Mount Video
# TODO: update for all Combatives videos and for W.E. and Master Cycle
from logging import warning

import pandas as pd
import requests
import re

# Define the base URL and segment range
subtitle_file_count = 200
base_url = "https://house-fastly-signed-us-east-1-prod.brightcovecdn.com/media/v1/hls/v4/clear/5853423584001/778089f8-1ad7-43ba-ba67-11c1a8234dc7/5c3861f8-b9f2-4d3f-a258-8d204f6e6e8c/segment"
token = ".vtt?fastly_token=NjcyMzI5YjJfYjdlMjRhMjc3ZWNkYjMxM2IzNjAyYjU1YWI2NTJiYmQ0Nzg0NzU3ZTcwMWM0OWE3ZTcxY2U3MjQ3OTM2MjdjZF8vL2hvdXNlLWZhc3RseS1zaWduZWQtdXMtZWFzdC0xLXByb2QuYnJpZ2h0Y292ZWNkbi5jb20vbWVkaWEvdjEvaGxzL3Y0L2NsZWFyLzU4NTM0MjM1ODQwMDEvNzc4MDg5ZjgtMWFkNy00M2JhLWJhNjctMTFjMWE4MjM0ZGM3LzVjMzg2MWY4LWI5ZjItNGQzZi1hMjU4LThkMjA0ZjZlNmU4Yy8%3D"

# Generate URLs for segments 0 to subtitle_file_count
urls = [f"{base_url}{i}{token}" for i in range(subtitle_file_count)]

# Use the urls to download the subtitles and assemble into one file
def pull_subtitles(url):
    response = requests.get(url)

    if response.status_code == 200:
        # Read the entire file content
        content = response.text

        # Alternatively, read the content in chunks
        # for chunk in response.iter_content(chunk_size=1024):

    else:
        content = "Webpage Data Pull Failed"
    return content


output = pd.DataFrame()
for url in urls:
    page_string = pull_subtitles(url)
    output = pd.concat([output, pd.DataFrame({'url': [url],
                                              'text': [page_string]})],
                       axis=0)


# TODO: combine files into one transcript
df_cleaned = output.copy()
df_cleaned['no_data_ind'] = [0 if i == 'Webpage Data Pull Failed' else 1 for i in list(df_cleaned['text'])]
print(df_cleaned['no_data_ind'].value_counts(dropna=False))

# Drop rows that don't exist
df_cleaned = df_cleaned[df_cleaned['no_data_ind']==1].reset_index(drop=True)

#Clean Text: remove timestamps, formatting, weird spacing
regex_pattern1 = r"\d{2}:\d{2}:\d{2}.\d{3}"
regex_pattern2 = r"\d{2}:\d{2}\.\d{3}"

df_cleaned['cleaned_text'] = df_cleaned['text']  # Initialize cleaned column
df_cleaned['cleaned_text'] = [re.sub(regex_pattern1, "", i) for i in list(df_cleaned['cleaned_text'])]  # Replaces time stamps
df_cleaned['cleaned_text'] = [re.sub(regex_pattern2, "", i) for i in list(df_cleaned['cleaned_text'])]  # Replaces time stamps
df_cleaned['cleaned_text'] = [i.replace("-->","") for i in list(df_cleaned['cleaned_text'])]  # Remove arrows
df_cleaned['cleaned_text'] = [i.replace("WEBVTT\nX-TIMESTAMP-MAP=LOCAL:00:,MPEGTS:0","") for i in list(df_cleaned['cleaned_text'])]  # Remove header string
df_cleaned['cleaned_text'] = [i.replace("WEBVTT\nX-TIMESTAMP-MAP=LOCAL:,MPEGTS:0","") for i in list(df_cleaned['cleaned_text'])]  # Remove 2nd header string
df_cleaned['cleaned_text'] = [i.replace("\n"," ") for i in list(df_cleaned['cleaned_text'])]  # Remove line breaks
df_cleaned['cleaned_text'] = [i.replace("\t"," ") for i in list(df_cleaned['cleaned_text'])]  # Remove tabs
df_cleaned['cleaned_text'] = [re.sub(' +', ' ', i) for i in list(df_cleaned['cleaned_text'])]  # Replace double+ spaces with single spaces
df_cleaned['cleaned_text'] = [i.strip() for i in list(df_cleaned['cleaned_text'])]  # Strip whitespace

# Combine rows into one string
str_cleaned = ' '.join(list(df_cleaned['cleaned_text']))

# Save Final Files (the df and the string)
df_cleaned.to_csv("./data/cleaned_data/video_transcripts_example_df.csv", index=False)
with open("./data/cleaned_data/video_transcripts/video_transcripts_example_str.txt", "w") as f:
    f.write(str_cleaned)

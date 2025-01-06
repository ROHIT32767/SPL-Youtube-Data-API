import pandas as pd
from googleapiclient.discovery import build
import isodate  # To parse ISO 8601 duration format
from difflib import SequenceMatcher  # For string similarity comparison
from openpyxl import load_workbook  # For appending to Excel files

API_KEY = 'AIzaSyA4QwaerJfYxLprMf44uGLZOZDk0CWFWG8'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def get_youtube_service():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def convert_duration_to_hours(duration):
    parsed_duration = isodate.parse_duration(duration)
    return parsed_duration.total_seconds() / 3600  # Convert seconds to hours

def is_similar(title1, title2, threshold=0.8):
    """
    Compare two titles to see if they are similar enough to be considered duplicates.
    Using SequenceMatcher to get a ratio of similarity.
    """
    return SequenceMatcher(None, title1, title2).ratio() > threshold

def search_videos_by_queries(language_query, queries, max_hours=1000):
    youtube = get_youtube_service()

    total_hours = 0
    videos_info = {}
    video_ids = set()

    for query in queries:
        if total_hours >= max_hours:
            break

        next_page_token = None

        while total_hours < max_hours:
            request = youtube.search().list(
                q=f"{language_query} {query}",  # Combine language and category
                type='video',
                videoDuration='any',
                part='snippet',
                maxResults=200,
                pageToken=next_page_token  # For pagination
            )
            response = request.execute()

            for item in response['items']:
                video_id = item['id']['videoId']

                # Get video details including duration and audio language
                video_request = youtube.videos().list(
                    part='contentDetails,snippet',
                    id=video_id
                )
                video_response = video_request.execute()

                if not video_response['items']:
                    continue  # Skip if video details are not available

                video_details = video_response['items'][0]

                title = video_details['snippet']['title']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                duration = video_details['contentDetails']['duration']

                default_audio_language = video_details['snippet'].get('defaultAudioLanguage')

                # # Only include videos that match the specified language
                # if default_audio_language != language_query.lower():
                #     continue

                # Convert duration to hours
                hours = convert_duration_to_hours(duration)

                if total_hours + hours > max_hours:
                    break

                # Avoid duplicates based on title similarity
                if any(is_similar(existing_title, title) for existing_title in videos_info):
                    continue

                videos_info[title] = {
                    'Title': title,
                    'URL': video_url,
                    'Duration': duration,
                    'Hours': hours,
                    'defaultAudioLanguage': default_audio_language,
                    'Category': query  # Add the category
                }

                total_hours += hours

                if total_hours >= max_hours:
                    break

            # Handle pagination if there are more pages of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break  # If no more pages, stop

            print(f"Collected {total_hours:.2f} hours so far for query '{query}'...")

    print(f"Finished collecting {total_hours:.2f} hours of videos for queries {queries}.")
    return list(videos_info.values())

def save_to_excel_append(language_videos, language_name, filename='final_language_videos_unique_1000_hours_v2.xlsx'):
    df = pd.DataFrame(language_videos)
    df['Cumulative Hours'] = df['Hours'].cumsum()
    total_hours = df['Hours'].sum()
    df.loc[len(df)] = ['Total', '', '', total_hours, total_hours, '', '']

    try:
        # Load the existing workbook and append the data
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'{language_name} Videos', index=False)
    except FileNotFoundError:
        # If file doesn't exist, create a new one
        with pd.ExcelWriter(filename, mode='w', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'{language_name} Videos', index=False)

    print(f"Data appended to {filename}")

if __name__ == '__main__':
    # Define the language and queries
    language_query = 'Arabic'  # Arabic
    queries = ['movies', 'songs', 'news', 'documentaries', 'series']

    # Search for videos
    arabic_videos = search_videos_by_queries(language_query=language_query, queries=queries, max_hours=1000)

    # Append to Excel
    save_to_excel_append(arabic_videos, 'Arabic')

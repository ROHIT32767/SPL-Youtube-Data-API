import pandas as pd
from googleapiclient.discovery import build
import isodate  # To parse ISO 8601 duration format
import os

API_KEY = 'AIzaSyCYTQdHJJEaL0moc0nTvKSE8cvcTD1x8WY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def get_youtube_service():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def convert_duration_to_hours(duration):
    parsed_duration = isodate.parse_duration(duration)
    return parsed_duration.total_seconds() / 3600  # Convert seconds to hours

def get_channel_id(channel_name):
    youtube = get_youtube_service()
    request = youtube.search().list(
        q=channel_name,
        type='channel',
        part='snippet',
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['id']['channelId']
    else:
        raise ValueError(f"Channel '{channel_name}' not found.")

def get_uploads_playlist_id(channel_id):
    youtube = get_youtube_service()
    request = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    else:
        raise ValueError(f"Uploads playlist for channel ID '{channel_id}' not found.")

def get_videos_from_playlist(playlist_id):
    youtube = get_youtube_service()
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            videos.append({
                'videoId': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title']
            })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

def get_video_details(video_ids):
    youtube = get_youtube_service()
    videos_info = []

    for i in range(0, len(video_ids), 50):  # API allows a maximum of 50 IDs per request
        request = youtube.videos().list(
            part='contentDetails,snippet',
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()

        for item in response['items']:
            duration = item['contentDetails']['duration']
            videos_info.append({
                'Title': item['snippet']['title'],
                'URL': f"https://www.youtube.com/watch?v={item['id']}",
                'Duration': duration,
                'Hours': convert_duration_to_hours(duration)
            })

    return videos_info


def save_to_excel(videos_info, language_name):
    filename = 'final_language_videos_unique_1000_hours.xlsx'

    # Check if the file exists and read it if it does
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename, sheet_name=f'{language_name} Videos')
    else:
        existing_df = pd.DataFrame()

    # Create a new DataFrame from the current videos info
    new_df = pd.DataFrame(videos_info)
    new_df['Cumulative Hours'] = new_df['Hours'].cumsum()
    total_hours = new_df['Hours'].sum()
    new_df.loc[len(new_df)] = ['Total', '', '', total_hours, total_hours]

    # Combine with the existing data
    if not existing_df.empty:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # Save the updated DataFrame to the file
    combined_df.to_excel(filename, sheet_name=f'{language_name} Videos', index=False)
    print(f"Data appended and saved to {filename}")


if __name__ == '__main__':
    language_name = "Arabic"
    channel_name = "Arabic Music Channel"

    try:
        # Get the channel ID
        channel_id = get_channel_id(channel_name)

        # Get the uploads playlist ID
        playlist_id = get_uploads_playlist_id(channel_id)

        # Get all videos from the playlist
        videos = get_videos_from_playlist(playlist_id)

        # Get detailed information for the videos
        video_ids = [video['videoId'] for video in videos]
        videos_info = get_video_details(video_ids)

        # Save to an Excel file
        save_to_excel(videos_info, language_name)

    except ValueError as e:
        print(e)


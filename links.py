import pandas as pd
from googleapiclient.discovery import build
import isodate  # To parse ISO 8601 duration format
from difflib import SequenceMatcher  # For string similarity comparison

API_KEY = 'AIzaSyBNokmw6meBvWhLoTmdB_5LSWzrlJ4vPQI'
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

def search_videos(language_query, max_hours=1000):
    youtube = get_youtube_service()
    
    total_hours = 0
    videos_info = {}
    video_ids = set()

    def collect_videos(query, max_hours, total_hours):
        nonlocal videos_info, video_ids
        next_page_token = None

        while total_hours < max_hours:
            request = youtube.search().list(
                q=query,  # Query for language-specific movies/news
                type='video',
                videoDuration='any',
                part='snippet',
                maxResults=50,
                pageToken=next_page_token  # For pagination
            )
            response = request.execute()

            for item in response['items']:
                video_id = item['id']['videoId']

                # Get video details including duration
                video_request = youtube.videos().list(
                    part='contentDetails,snippet',
                    id=video_id
                )
                video_response = video_request.execute()
                video_details = video_response['items'][0]
                
                title = video_details['snippet']['title']
                description = video_details['snippet']['description']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                duration = video_details['contentDetails']['duration']

                defaultLanguage = None
                defaultAudioLanguage = None
                
                if video_response['items']:
                    snippet_data = video_response['items'][0]['snippet']
                    defaultLanguage = snippet_data.get('defaultLanguage', None)
                    defaultAudioLanguage = snippet_data.get('defaultAudioLanguage', None)
                
                # Convert duration to hours
                hours = convert_duration_to_hours(duration)
                
                if total_hours + hours > max_hours:
                    break

                # Check if a similar video (based on title) already exists
                found_similar = False
                for existing_title, existing_video in videos_info.items():
                    if is_similar(existing_title, title):
                        # If the new video has a longer duration, replace the existing one
                        if hours > existing_video['Hours']:
                            videos_info[existing_title] = {
                                'Title': title,
                                'URL': video_url,
                                'Duration': duration,
                                'Hours': hours,
                                'defaultLanguage': defaultLanguage,
                                'defaultAudioLanguage': defaultAudioLanguage
                            }
                        found_similar = True
                        break

                if not found_similar:
                    # If no similar video found, add this one
                    videos_info[title] = {
                        'Title': title,
                        'URL': video_url,
                        'Duration': duration,
                        'Hours': hours,
                        'defaultLanguage': defaultLanguage,
                        'defaultAudioLanguage': defaultAudioLanguage
                    }
                    total_hours += hours

                video_ids.add(video_id)  # Add video ID to set of unique videos

            # Handle pagination if there are more pages of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break  # If no more pages, stop

            print(f"Collected {total_hours:.2f} hours so far for query '{query}'...")

        return total_hours

    # Collect movies first
    total_hours = collect_videos(f'{language_query} movies', max_hours, total_hours)

    # Then collect news if still under max_hours
    if total_hours < max_hours:
        total_hours = collect_videos(f'{language_query} news', max_hours, total_hours)

    print(f"Finished collecting {total_hours:.2f} hours of videos for query '{language_query}'.")
    return list(videos_info.values())

def save_to_excel(marathi_videos, urdu_videos, arabic_videos):
    with pd.ExcelWriter('final_language_videos_unique_1000_hours.xlsx') as writer:
        # Process Marathi Videos
        marathi_df = pd.DataFrame(marathi_videos)
        marathi_df['Cumulative Hours'] = marathi_df['Hours'].cumsum()  # Add cumulative hours column
        marathi_total_hours = marathi_df['Hours'].sum()
        marathi_df.loc[len(marathi_df)] = ['Total', '', '', marathi_total_hours, marathi_total_hours]  # Final row for total hours
        marathi_df.to_excel(writer, sheet_name='Marathi Videos', index=False)

        # Process Urdu Videos
        urdu_df = pd.DataFrame(urdu_videos)
        urdu_df['Cumulative Hours'] = urdu_df['Hours'].cumsum()  # Add cumulative hours column
        urdu_total_hours = urdu_df['Hours'].sum()
        urdu_df.loc[len(urdu_df)] = ['Total', '', '', urdu_total_hours, urdu_total_hours]  # Final row for total hours
        urdu_df.to_excel(writer, sheet_name='Urdu Videos', index=False)

        # Process Arabic Videos
        arabic_df = pd.DataFrame(arabic_videos)
        arabic_df['Cumulative Hours'] = arabic_df['Hours'].cumsum()
        arabic_total_hours = arabic_df['Hours'].sum()
        arabic_df.loc[len(arabic_df)] = ['Total', '', '', arabic_total_hours, arabic_total_hours]
        arabic_df.to_excel(writer, sheet_name='Arabic Videos', index=False)

    print(f"Data saved to language_videos_unique_1000_hours.xlsx with total durations for Marathi and Urdu.")

if __name__ == '__main__':
    # Search for Marathi movies and news
    marathi_videos = search_videos(language_query='Marathi', max_hours=1000)
    
    # Search for Urdu movies and news
    urdu_videos = search_videos(language_query='Urdu', max_hours=1000)

    # Search for Arabic movies and news
    arabic_videos = search_videos(language_query='Arabic', max_hours=1000)
    
    # Save both datasets to the same Excel file in two different sheets
    save_to_excel(marathi_videos, urdu_videos, arabic_videos)
    
    print('Data saved to language_videos_unique_1000_hours.xlsx')
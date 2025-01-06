import pandas as pd

def filter_unique_non_null_urls(filename):
    # Read the existing Excel file
    try:
        df = pd.read_excel(filename)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Filter rows where defaultAudioLanguage is 'ar' or null
    df_filtered = df[(df['defaultAudioLanguage'].isnull()) | (df['defaultAudioLanguage'] == 'ar')]

    # Filter rows with non-null URLs
    filtered_df = df_filtered[df_filtered['URL'].notnull()]

    # Remove duplicate URLs, keeping the first occurrence
    filtered_df = filtered_df.drop_duplicates(subset='URL', keep='first')

    # Remove rows with 'Category' attribute equal to 'songs' with 'Hours' less than 0.05

    filtered_df = filtered_df[~((filtered_df['Category'] == 'songs') & (filtered_df['Hours'] < 0.1))]

    # Reset the index
    filtered_df.reset_index(drop=True, inplace=True)

    # Print the sum of all 'Hours' columns
    print(f"Total Duration: {filtered_df['Hours'].sum()}")

    # Save the filtered DataFrame back to the Excel file
    with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
        filtered_df.to_excel(writer, index=False)

    print(f"Filtered data saved to '{filename}'. The sheet now contains unique and non-null URLs.")

# Usage
filename = 'final_language_videos_unique_1000_hours.xlsx'
filter_unique_non_null_urls(filename)

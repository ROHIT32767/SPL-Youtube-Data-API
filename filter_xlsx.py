import pandas as pd

def filter_unique_non_null_urls(filename, sheet_name='Sheet1'):
    # Read the existing Excel file
    try:
        df = pd.read_excel(filename, sheet_name=sheet_name)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Filter rows with non-null URLs
    filtered_df = df[df['URL'].notnull()]

    # Remove duplicate URLs, keeping the first occurrence
    filtered_df = filtered_df.drop_duplicates(subset='URL', keep='first')

    # Reset the index
    filtered_df.reset_index(drop=True, inplace=True)

    # print the sum of all 'Hours' columns
    print(f"Total Duration: {filtered_df['Hours'].sum()}")

    # Save the filtered DataFrame back to the Excel file
    with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
        filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Filtered data saved to '{filename}'. The sheet now contains unique and non-null URLs.")

# Usage
filename = 'final_language_videos_unique_1000_hours.xlsx'
sheet_name = 'Arabic Videos'  # Replace with the appropriate sheet name if necessary
filter_unique_non_null_urls(filename, sheet_name)

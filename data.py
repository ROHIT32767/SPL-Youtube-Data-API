import pandas as pd

# Load the first Excel file
df1 = pd.read_excel('final_language_videos_unique_1000_hours.xlsx')

# Load the second Excel file
df2 = pd.read_excel('final_language_videos_unique_1000_hours_v2.xlsx')

# Append rows from df2 to df1
df_combined = pd.concat([df1, df2], ignore_index=True)

# Save the combined DataFrame back to the first Excel file
df_combined.to_excel('final_language_videos_unique_1000_hours.xlsx', index=False)

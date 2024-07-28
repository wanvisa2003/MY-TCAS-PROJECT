import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('./data/university.csv')

# Filter rows where the 'major', 'depart', 'course', or 'thai_name' columns contain the keyword 'วิศวกรรม'
major_df = df[df['major'].str.contains('วิศวกรรม', na=False)]
depart_df = df[df['depart'].str.contains('วิศวกรรม', na=False)]
course_df = df[df['course'].str.contains('วิศวกรรม', na=False)]
thai_name_df = df[df['thai_name'].str.contains('วิศวกรรม', na=False)]

# Combine the filtered DataFrames and remove duplicates
combine_df = pd.concat([major_df, depart_df, course_df, thai_name_df])
combine_df = combine_df.drop_duplicates()

# Columns to delete from the combined DataFrame
delete_columns = ['web-scraper-order', 'web-scraper-start-url', 'uni-href', 'major-href', 'depart-href', 'course-href', 'thai_name']
main_df = combine_df.drop(columns=delete_columns)

# Clean up specific columns by removing numerical prefixes and extracting numerical values
# remove 1. 2. 3.
main_df['major'] = main_df['major'].str.replace(r'\d+\.\s*', '', regex=True)
main_df['depart'] = main_df['depart'].str.replace(r'\d+\.\s*', '', regex=True)
main_df['course'] = main_df['course'].str.replace(r'\d+\.\s*', '', regex=True)
# store only number and fill na with 0
main_df['fee'] = main_df['fee'].str.extract(r'(\d[\d,]*)').replace(',', '', regex=True)
main_df['round1'] = main_df['round1'].str.extract(r'(\d+)')
main_df['round2'] = main_df['round2'].str.extract(r'(\d+)')
main_df['round3'] = main_df['round3'].str.extract(r'(\d+)')
main_df['round4'] = main_df['round4'].str.extract(r'(\d+)')
main_df = main_df.fillna(0)

# Convert columns to appropriate data types
main_df['fee'] = main_df['fee'].astype(int)
main_df['round1'] = main_df['round1'].astype(int)
main_df['round2'] = main_df['round2'].astype(int)
main_df['round3'] = main_df['round3'].astype(int)
main_df['round4'] = main_df['round4'].astype(int)

# Adjust fees by convert 1 semesters fees to 8 semester fees (4 years) 
main_df.loc[main_df['fee'] < 80000, 'fee'] = main_df['fee'] * 8


# Save the merged DataFrame to a new CSV file
try:
    main_df.to_csv('./data/engineer_data.csv', index=False)
    print("Save success!")
except Exception as e:
    print(f"Save failed: {e}")
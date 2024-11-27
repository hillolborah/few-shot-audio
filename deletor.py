import pandas as pd

# Define the file path of the CSV
csv_file = "Data_Analysis/extracted_features.csv"  # Replace with the path to your CSV file

# Define the entries to be removed
entries_to_remove = ['Tick', 'Wind', 'Wind noise (Microphone)']  # Replace with your specific entries

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file)

# Filter the DataFrame to exclude rows with specific entries in the 'subdirectory' column
df_filtered = df[~df['Subdirectory'].isin(entries_to_remove)]

# Save the filtered DataFrame back to a CSV file
output_file = "filtered_file.csv"  # Replace with the desired output file path
df_filtered.to_csv(output_file, index=False)

print(f"Rows containing {entries_to_remove} in the 'subdirectory' column have been removed.")
print(f"Filtered CSV saved to {output_file}.")

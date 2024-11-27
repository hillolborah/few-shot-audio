import os
import csv

# Define the paths to the two main folders
folder1 = 'emergency sounds'  # Replace with actual path
folder2 = 'normal sounds'  # Replace with actual path

# Function to count files in a directory
def count_files_in_directory(directory):
    try:
        # List all files in the directory and count them
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    except FileNotFoundError:
        return 0  # Return 0 if the folder is not found

# Function to iterate through all subdirectories and count files
def count_files_in_folders(base_folder):
    directory_data = []
    for subdir, _, _ in os.walk(base_folder):
        # Count files in each subdirectory
        file_count = count_files_in_directory(subdir)
        # Add directory and its file count to the list
        directory_data.append([subdir, file_count])
    return directory_data

# Get the file counts for all directories in both folders
folder1_data = count_files_in_folders(folder1)
folder2_data = count_files_in_folders(folder2)

# Prepare the data for the CSV
data = [['Directory', 'File Count']]  # Header row
data.extend(folder1_data)  # Add data from folder1
data.extend(folder2_data)  # Add data from folder2

# Write the data to a CSV file
output_csv = 'directory_file_count_report_3.csv'  # Output file name
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"CSV report '{output_csv}' created successfully.")

import os
import pandas as pd
from pydub import AudioSegment
from multiprocessing import Pool, cpu_count

# Define your main folders
main_folders = ['emergency sounds', 'normal sounds']

# Function to process a single directory's CSV file
def process_directory(root, file):
    file_count = {}
    wav_files_to_delete = []
    
    # Read the CSV file
    csv_path = os.path.join(root, file)
    df = pd.read_csv(csv_path)
    
    # Iterate through each row in the CSV file
    for _, row in df.iterrows():
        # Extract the base name before the last underscore in the first column
        wav_base_name = row[0].rsplit('_', 1)[0]
        try:
            start_time = float(row[1]) * 1000  # Convert seconds to milliseconds
            end_time = float(row[2]) * 1000    # Convert seconds to milliseconds
        except ValueError:
            print("Error: One of the values in row[1] or row[2] is not a valid number.")
            continue
        
        # Check if the trimmed version already exists
        file_count[wav_base_name] = file_count.get(wav_base_name, 0) + 1
        unique_suffix = file_count[wav_base_name]
        output_path = os.path.join(root, f"{wav_base_name}_{unique_suffix}.wav")
        
        # If the trimmed audio file already exists, skip trimming this audio
        if os.path.exists(output_path):
            print(f"Trimmed file already exists: {output_path}. Skipping this file.")
            continue
        
        # Construct the .wav file path
        wav_file_path = os.path.join(root, f"{wav_base_name}.wav")
        
        # Check if the .wav file exists
        if os.path.exists(wav_file_path):
            # Load the audio file
            audio = AudioSegment.from_wav(wav_file_path)
            
            # Trim the audio
            trimmed_audio = audio[start_time:end_time]
            
            # Export the trimmed audio
            trimmed_audio.export(output_path, format="wav")
            print(f"Trimmed audio saved: {output_path}")
            
            # Add the original wav file path to the list for deletion later
            if wav_file_path not in wav_files_to_delete:
                wav_files_to_delete.append(wav_file_path)
        else:
            print(f"Wav file not found: {wav_file_path}")
    
    # Return the list of files to delete
    return wav_files_to_delete

# Function to delete wav files after processing all directories
def delete_wav_files(wav_files_to_delete):
    for wav_file in wav_files_to_delete:
        os.remove(wav_file)
        print(f"Deleted original audio file: {wav_file}")

# Main function to handle parallel processing
def parallel_process():
    # Collect all tasks (CSV files in the directories)
    tasks = []
    for main_folder in main_folders:
        for root, dirs, files in os.walk(main_folder):
            for file in files:
                if file.endswith('.csv'):
                    tasks.append((root, file))
    
    # Use multiprocessing to process CSV files in parallel
    with Pool(processes=75) as pool:
        results = pool.starmap(process_directory, tasks)
    
    # Flatten the list of results and delete original wav files
    all_wav_files_to_delete = [item for sublist in results for item in sublist]
    delete_wav_files(all_wav_files_to_delete)

if __name__ == "__main__":
    parallel_process()

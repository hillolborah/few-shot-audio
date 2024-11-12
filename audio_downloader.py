import yt_dlp
from pydub import AudioSegment
import os
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed

def get_video_id_and_start_time(file_string):
    """Extract YouTube ID and start time from the format like 'zfI3S4Pgqg0_5000'."""
    try:
        ytid, start_time = file_string.split('_')
        start_time = int(start_time) / 1000.0  # Convert to seconds (from milliseconds)
        return ytid.strip(), start_time
    except ValueError:
        print(f"Invalid format in the string: {file_string}")
        return None, None

def count_files_in_directory(directory):
    """Count the number of files in a directory."""
    return sum(len(files) for _, _, files in os.walk(directory))

def extract_audio_segment(video_id, start_time, end_time, output_folder):
    """Download and trim the audio segment."""
    # Check if the total number of files in the output folder is less than 1004
    if count_files_in_directory(output_folder) >= 1004:
        print(f"Total number of files in {output_folder} has reached or exceeded 1004. Skipping video {video_id}.")
        return
    audio_file = f"{output_folder}/{video_id}.wav" 
    if os.path.exists(audio_file):
        print(f"{video_id}.wav Already Exists")
        return
    # yt-dlp options to download the best audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'wav',
        'outtmpl': f'{output_folder}/{video_id}.%(ext)s',  # Save in the CSV folder
        'ffmpeg_location': 'C:/ffmpeg',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    # Download the audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            audio_file = f"{output_folder}/{video_id}.wav"

        # Load the audio file and trim it using Pydub
        audio = AudioSegment.from_wav(audio_file)
        start_time_ms = start_time * 1000  # Convert to milliseconds
        end_time_ms = end_time * 1000

        trimmed_audio = audio[start_time_ms:end_time_ms]

        # Export the trimmed audio back to the same file or a new file
        trimmed_audio.export(audio_file, format="wav")
        print(f"Trimmed audio saved as: {audio_file}")
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}")
        continue

def process_single_entry(csv_file):
    """Process one CSV entry."""
    csv_folder = os.path.dirname(csv_file)

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("CSV Headers:", reader.fieldnames)

        # Process only the first row in the CSV for testing
        row = next(reader, None)  # Fetch the first row
        if row:
            file_string = row[' segment_id'].strip()  # Extract the string like 'zfI3S4Pgqg0_5000'
            video_id, start_time = get_video_id_and_start_time(file_string)
            if video_id is not None and start_time is not None:
                try:
                    end_time = start_time + 10
                    extract_audio_segment(video_id, start_time, end_time, csv_folder)
                except ValueError:
                    print(f"Skipping video {video_id}: Invalid end time.")
        else:
            print("No data found in the CSV file.")

def process_csv_files_in_folder(folder):
    """Iterate through all directories and process CSV files found."""
    csv_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.csv'):
                csv_file = os.path.join(root, file)
                csv_files.append(csv_file)
    return csv_files

def process_folders_in_parallel(folders, num_cores=70):
    """Process the folders in parallel using multiple cores."""
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        
        for folder in folders:
            csv_files = process_csv_files_in_folder(folder)
            for csv_file in csv_files:
                futures.append(executor.submit(process_single_entry, csv_file))
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # Will raise an exception if processing failed
            except Exception as e:
                print(f"Error during processing: {e}")
                continue

def main():
    # Define the main folders containing subfolders with CSV files
    main_folders = ['emergency sounds', 'normal sounds']

    # Process the folders in parallel (60 cores)
    process_folders_in_parallel(main_folders, num_cores=60)

if __name__ == "__main__":
    main()

import os
import librosa
import numpy as np
import pandas as pd
from math import ceil
from concurrent.futures import ProcessPoolExecutor

# Paths to the two main folders
main_folders = ["../emergency sounds", "../normal sounds"]

# Function to extract features from a single audio file
def extract_features(audio_file, main_folder_name, subdirectory_name):
    try:
        # Load the audio file
        y, sr = librosa.load(audio_file, sr=None)

        # Check if the loaded audio signal is empty
        if y.size == 0:
            print(f"Warning: {audio_file} is empty or corrupted.")
            return None

        # Extract MFCCs
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)

        # Extract Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        # Extract Spectral Contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        spectral_contrast_mean = np.mean(spectral_contrast, axis=1)

        # Extract other features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y=y))
        rms = np.mean(librosa.feature.rms(y=y))
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Extract pitch
        pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
        pitch = np.max(pitches) if pitches.size > 0 else 0

        # Store features in a dictionary
        feature_dict = {
            'File': os.path.basename(audio_file),
            'Main_Folder': main_folder_name,
            'Subdirectory': subdirectory_name,
            'MFCC_1': mfcc_mean[0], 'MFCC_2': mfcc_mean[1], 'MFCC_3': mfcc_mean[2], 'MFCC_4': mfcc_mean[3],
            'MFCC_5': mfcc_mean[4], 'MFCC_6': mfcc_mean[5], 'MFCC_7': mfcc_mean[6], 'MFCC_8': mfcc_mean[7],
            'MFCC_9': mfcc_mean[8], 'MFCC_10': mfcc_mean[9], 'MFCC_11': mfcc_mean[10], 'MFCC_12': mfcc_mean[11],
            'MFCC_13': mfcc_mean[12],
            'Chroma_1': chroma_mean[0], 'Chroma_2': chroma_mean[1], 'Chroma_3': chroma_mean[2], 'Chroma_4': chroma_mean[3],
            'Chroma_5': chroma_mean[4], 'Chroma_6': chroma_mean[5], 'Chroma_7': chroma_mean[6], 'Chroma_8': chroma_mean[7],
            'Chroma_9': chroma_mean[8], 'Chroma_10': chroma_mean[9], 'Chroma_11': chroma_mean[10], 'Chroma_12': chroma_mean[11],
            'Spectral_Contrast_1': spectral_contrast_mean[0], 'Spectral_Contrast_2': spectral_contrast_mean[1],
            'Spectral_Contrast_3': spectral_contrast_mean[2], 'Spectral_Contrast_4': spectral_contrast_mean[3],
            'Spectral_Contrast_5': spectral_contrast_mean[4], 'Spectral_Contrast_6': spectral_contrast_mean[5],
            'Spectral_Contrast_7': spectral_contrast_mean[6],
            'Spectral_Centroid': spectral_centroid,
            'Spectral_Bandwidth': spectral_bandwidth,
            'Spectral_Rolloff': spectral_rolloff,
            'Zero_Crossing_Rate': zero_crossing_rate,
            'RMS': rms,
            'Tempo': tempo,
            'Pitch': pitch,
        }

        print(f"Features extracted for {audio_file}")
        return feature_dict
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return None

# Function to process a chunk of files
def process_files_chunk(task):
    files, main_folder_name, subdirectory_name = task
    features_list = []
    for audio_file in files:
        features = extract_features(audio_file, main_folder_name, subdirectory_name)
        if features:
            features_list.append(features)
    return features_list

# Function to split files into two chunks for two cores
def split_files(files, num_chunks=2):
    if len(files) == 0:
        return []  # Return an empty list if no files are found
    chunk_size = ceil(len(files) / num_chunks)
    return [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

# Main function to parallelize processing across directories
def main():
    tasks = []
    for main_folder in main_folders:
        for root, _, files in os.walk(main_folder):
            subdirectory_name = os.path.relpath(root, main_folder)
            wav_files = [os.path.join(root, file) for file in files if file.endswith(".wav")]
            chunks = split_files(wav_files, 2)
            if not chunks:  # Skip if no chunks (empty directory)
                continue
            for chunk in chunks:
                tasks.append((chunk, os.path.basename(main_folder), subdirectory_name))

    # Parallelize processing using ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        futures = executor.map(process_files_chunk, tasks)

    # Gather all features
    all_features = []
    for result in futures:
        if result:
            all_features.extend(result)

    # Convert the list of features dictionaries to a DataFrame
    df = pd.DataFrame(all_features)

    # Save the DataFrame to a CSV file
    df.to_csv("extracted_features.csv", index=False)
    print("Feature extraction complete. Saved to extracted_features.csv")

if __name__ == "__main__":
    main()

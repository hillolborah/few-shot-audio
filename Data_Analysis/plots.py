import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
from concurrent.futures import ProcessPoolExecutor

# Load the extracted features CSV
csv_path = "extracted_features.csv"
df = pd.read_csv(csv_path)

# Create directories for saving the plots based on 'Main_Folder' and 'Subdirectory' columns
def create_save_directories(df):
    save_dirs = {}
    
    for main_folder in df['Main_Folder'].unique():
        main_folder_path = os.path.join("visualizations", main_folder)
        if not os.path.exists(main_folder_path):
            os.makedirs(main_folder_path)
        
        # Create Subdirectory under each 'Main_Folder'
        sub_dir_names = df[df['Main_Folder'] == main_folder]['Subdirectory'].unique()
        for sub_dir in sub_dir_names:
            sub_dir_path = os.path.join(main_folder_path, sub_dir)
            if not os.path.exists(sub_dir_path):
                os.makedirs(sub_dir_path)
            # Create specific Subdirectory for different types of graphs
            for graph_type in ['zcr_rms', 'centroid_bandwidth', 'pitch', 'contrast_chroma']:
                graph_dir = os.path.join(sub_dir_path, graph_type)
                if not os.path.exists(graph_dir):
                    os.makedirs(graph_dir)
            
            save_dirs[(main_folder, sub_dir)] = sub_dir_path
    
    return save_dirs

# Get save directories for each combination of Main_Folder and Subdirectory
save_dirs = create_save_directories(df)

# Visualization functions

def visualize_contrast_chroma(row):
    # Compute the mean of Spectral Contrast (1 to 7) and Chroma (1 to 12)
    spectral_contrast_mean = [
        row['Spectral_Contrast_1'],
        row['Spectral_Contrast_2'],
        row['Spectral_Contrast_3'],
        row['Spectral_Contrast_4'],
        row['Spectral_Contrast_5'],
        row['Spectral_Contrast_6'],
        row['Spectral_Contrast_7']
    ]
    chroma_mean = [
        row['Chroma_1'],
        row['Chroma_2'],
        row['Chroma_3'],
        row['Chroma_4'],
        row['Chroma_5'],
        row['Chroma_6'],
        row['Chroma_7'],
        row['Chroma_8'],
        row['Chroma_9'],
        row['Chroma_10'],
        row['Chroma_11'],
        row['Chroma_12']
    ]
    
    # Calculate the mean of spectral contrast and chroma
    spectral_contrast_mean = np.mean(spectral_contrast_mean)
    chroma_mean = np.mean(chroma_mean)
    
    # Create the plot
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    
    # Spectral Contrast Plot
    ax[0].bar(['Spectral Contrast'], [spectral_contrast_mean], color='blue')
    ax[0].set_title(f'Spectral Contrast Mean of {row["File"]}')
    ax[0].set_ylabel('Spectral Contrast (dB)')
    
    # Chroma Plot
    ax[1].bar(['Chroma'], [chroma_mean], color='green')
    ax[1].set_title(f'Chroma Mean of {row["File"]}')
    ax[1].set_ylabel('Chroma Intensity')

    plt.tight_layout()
    
    # Save the plot in the appropriate subdirectory
    save_path = os.path.join(save_dirs[(row['Main_Folder'], row['Subdirectory'])], "contrast_chroma", f"{row['File']}_contrast_chroma.png")
    plt.savefig(save_path)
    plt.close()
    
    # Print confirmation
    print(f"Plotted and saved: {row['File']}_contrast_chroma.png")

def visualize_zcr_rms(row):
    zcr = np.array(ast.literal_eval(row["Zero_Crossing_Rate"]))
    rms = np.array(ast.literal_eval(row["RMS"]))
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    ax[0].plot(zcr, color='green')
    ax[0].set_title(f'Zero-Crossing Rate of {row["File"]}')
    
    ax[1].plot(rms, color='red')
    ax[1].set_title(f'RMS Energy of {row["File"]}')
    
    plt.tight_layout()
    save_path = os.path.join(save_dirs[(row['Main_Folder'], row['Subdirectory'])], "zcr_rms", f"{row['File']}_zcr_rms.png")
    plt.savefig(save_path)
    plt.close()
    
    # Print confirmation
    print(f"Plotted and saved: {row['File']}_zcr_rms.png")

def visualize_centroid_bandwidth(row):
    spectral_centroid = np.array(ast.literal_eval(row["Spectral_Centroid"]))
    spectral_bandwidth = np.array(ast.literal_eval(row["Spectral_Bandwidth"]))
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    ax[0].plot(spectral_centroid, color='blue')
    ax[0].set_title(f'Spectral Centroid of {row["File"]}')
    
    ax[1].plot(spectral_bandwidth, color='purple')
    ax[1].set_title(f'Spectral Bandwidth of {row["File"]}')
    
    plt.tight_layout()
    save_path = os.path.join(save_dirs[(row['Main_Folder'], row['Subdirectory'])], "centroid_bandwidth", f"{row['File']}_centroid_bandwidth.png")
    plt.savefig(save_path)
    plt.close()
    
    # Print confirmation
    print(f"Plotted and saved: {row['File']}_centroid_bandwidth.png")

def visualize_pitch(row):
    pitches = np.array(ast.literal_eval(row["Pitch"]))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(np.max(pitches, axis=0), color='orange')
    ax.set_title(f'Pitch Detection of {row["File"]}')
    ax.set_ylabel('Pitch (Hz)')
    
    plt.tight_layout()
    save_path = os.path.join(save_dirs[(row['Main_Folder'], row['Subdirectory'])], "pitch", f"{row['File']}_pitch.png")
    plt.savefig(save_path)
    plt.close()
    
    # Print confirmation
    print(f"Plotted and saved: {row['File']}_pitch.png")

# Process each row for visualization
def process_row(row):
    visualize_contrast_chroma(row)
    visualize_zcr_rms(row)
    visualize_centroid_bandwidth(row)
    visualize_pitch(row)

# Parallel Processing (Optional)
if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=75) as executor:
        executor.map(process_row, [row for _, row in df.iterrows()])

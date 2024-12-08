import os
import pandas as pd

# Directories containing the spectrograms
emergency_dir = "/mnt/c/Users/jayant-few-shot/Few_shot/new-sounds/emergency-sounds/emergency_spectrograms"
normal_dir = "/mnt/c/Users/jayant-few-shot/Few_shot/new-sounds/normal-sounds/spectogram_normal_sounds"

# Output CSV file paths
emergency_csv = "/mnt/c/Users/jayant-few-shot/Few_shot/spectogram_to_csv/emergency_sounds_labels.csv"
normal_csv = "/mnt/c/Users/jayant-few-shot/Few_shot/spectogram_to_csv/normal_sounds_labels.csv"

def generate_csv(directory, label, output_csv):
    data = []
    for file in os.listdir(directory):
        if file.endswith(".png"):  # Ensure it's a spectrogram image file
            file_path = os.path.join(directory, file)
            data.append({"file_path": file_path, "label": label})
    # Save the data to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"CSV file created: {output_csv}")

# Generate CSV for emergency sounds
generate_csv(emergency_dir, "emergency", emergency_csv)

# Generate CSV for normal sounds
generate_csv(normal_dir, "normal", normal_csv)

import os
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from pydub.effects import normalize
import random
from concurrent.futures import ProcessPoolExecutor


def augment_audio(file_path, output_dir, aug_type, base_name, index):
    """
    Augments an audio file by applying a random transformation.
    Saves augmented files in the same directory.
    
    Args:
    - file_path: Path to the input .wav file.
    - output_dir: Directory to save augmented files.
    - aug_type: Type of augmentation (e.g., 'speed', 'noise', 'pitch', 'echo').
    - base_name: Base name of the original file (without extension).
    - index: The index of the augmentation (for uniqueness).
    """
    # Load audio
    audio = AudioSegment.from_wav(file_path)
    
    augmented_audio = None

    if aug_type == 'speed':
        speed_factor = random.uniform(0.8, 1.2)
        augmented_audio = audio.speedup(playback_speed=speed_factor)
    elif aug_type == 'noise':
        noise = WhiteNoise().to_audio_segment(duration=len(audio), volume=-25)
        augmented_audio = audio.overlay(noise)
    elif aug_type == 'pitch':
        pitch_semitones = random.randint(-5, 5)
        augmented_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * (2.0 ** (pitch_semitones / 12.0)))
        }).set_frame_rate(audio.frame_rate)
    elif aug_type == 'echo':
        def add_echo(audio, delay_ms=500, decay=0.6):
            echo = audio - 10
            combined = audio.overlay(echo, position=delay_ms)
            return normalize(combined)
        augmented_audio = add_echo(audio)

    # Save augmented file with the format filename_{aug_type}_{index}.wav
    output_file = os.path.join(output_dir, f"{base_name}_{aug_type}_{index}.wav")
    augmented_audio.export(output_file, format="wav")


def process_directory(subdir, target_count):
    """
    Augments files in a single directory until the target count is met,
    processing the largest files first, ensuring each file is augmented only once.
    
    Args:
    - subdir: The directory to process.
    - target_count: Total number of files required.
    """
    # Get .wav files in the directory with their file sizes
    files = [(f, os.path.getsize(os.path.join(subdir, f))) for f in os.listdir(subdir) if f.endswith('.wav')]
    
    # Sort files by size in descending order
    files.sort(key=lambda x: x[1], reverse=True)

    current_count = len(files)

    if current_count >= target_count:
        print(f"Directory '{subdir}' already has {current_count} files. Skipping...")
        return

    files_needed = target_count - current_count
    print(f"Directory '{subdir}' needs {files_needed} more files. Augmenting...")

    augmented_files = set()  # Track which files have been augmented

    for file, _ in files:
        if files_needed <= 0:
            break

        file_path = os.path.join(subdir, file)
        base_name = os.path.splitext(os.path.basename(file))[0]

        # Check if this file has already been augmented
        if file in augmented_files:
            continue

        # Apply augmentation
        for i in range(files_needed):
            aug_type = random.choice(['speed', 'noise', 'pitch', 'echo'])
            augment_audio(file_path, subdir, aug_type, base_name, i)
        
        augmented_files.add(file)  # Mark this file as augmented
        files_needed -= 1

    print(f"Finished augmenting directory: {subdir}")


def process_directories_parallel(main_folders, target_count=1500, max_workers=75):
    """
    Processes all subdirectories in the main folders in parallel, prioritizing large files.
    
    Args:
    - main_folders: List of paths to main folders.
    - target_count: Total number of files required in each directory.
    - max_workers: Number of parallel processes to use.
    """
    subdirectories = []

    # Collect all subdirectories
    for main_folder in main_folders:
        for subdir, _, files in os.walk(main_folder):
            if any(f.endswith('.wav') for f in files):  # Check for .wav files
                subdirectories.append(subdir)

    # Process subdirectories in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_directory, subdirectories, [target_count] * len(subdirectories))


# Main execution
main_folders = ["../emergency sounds", "../normal sounds"]  # Replace with your main folders
process_directories_parallel(main_folders, target_count=1500, max_workers=75)
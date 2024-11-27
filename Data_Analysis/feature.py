import librosa
import numpy as np

# Function to extract features from a single audio file
def extract_features_from_file(file_path):
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)

        # Dictionary to store features
        features = {}

        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i, mfcc in enumerate(mfccs, start=1):
            features[f'MFCC_{i}'] = np.mean(mfcc)

        # Extract Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        for i, ch in enumerate(chroma, start=1):
            features[f'Chroma_{i}'] = np.mean(ch)

        # Extract Spectral Contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        for i, cont in enumerate(contrast, start=1):
            features[f'Spectral_Contrast_{i}'] = np.mean(cont)

        # Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['Spectral_Centroid'] = np.mean(spectral_centroid)

        # Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features['Spectral_Bandwidth'] = np.mean(spectral_bandwidth)

        # Spectral Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features['Spectral_Rolloff'] = np.mean(spectral_rolloff)

        # Zero Crossing Rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        features['Zero_Crossing_Rate'] = np.mean(zero_crossing_rate)

        # RMS (Root Mean Square Energy)
        rms = librosa.feature.rms(y=y)
        features['RMS'] = np.mean(rms)

        # Tempo (BPM)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        features['Tempo'] = tempo

        # Pitch (Estimated Fundamental Frequency)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch = np.max(pitches) if pitches.any() else 0
        features['Pitch'] = pitch

        return features

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

# Path to your .wav file
file_path = "../emergency sounds/Alarm/_CTWgEciJBE_1.wav"

# Extract features
features = extract_features_from_file(file_path)

# Print features
if features:
    print("Extracted Features:")
    for key, value in features.items():
        print(f"{key}: {value}")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter


FILEPATH = "Messungen"

# 1) Daten laden
def load_data():
    file_number = input("Welche Messung soll analysiert werden? -- ")
    data = scipy.io.loadmat(f"{FILEPATH}/{file_number}")

    if not isinstance(data, dict):
        raise Exception("The read in File has the wrong format")
    try:
        sample_time = data["vSampleTime"][0]
        sample_vCuffPressure = data["vCuffPressure"][0]
    except KeyError or IndexError:
        raise Exception("The read in File has the wrong format")

    begin_index = np.where(sample_time == 3)[0][0]
    end_index = np.where(sample_vCuffPressure == np.max(sample_vCuffPressure))[0][0]
    return sample_time[begin_index:end_index], sample_vCuffPressure[begin_index:end_index]

# 2) Bandpass-Filter
def bandpass_filter(signal, fs=200.0, low=0.7, high=5.0, order=3):
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)

# 3) Envelope via Hilbert-Transformation
def compute_envelope(filtered_signal, smooth_window=101, smooth_poly=3):
    analytic = hilbert(filtered_signal)
    envelope = np.abs(analytic)
    envelope_smooth = savgol_filter(envelope, smooth_window, smooth_poly)
    return envelope_smooth

# 4) Peaks und Amplitude-vs-Druck-Kurve erzeugen
def extract_peak_amplitudes(envelope, raw_pressure, fs=200.0):
    peaks, _ = find_peaks(envelope, distance=int(0.4*fs))  # mind. ~0.4s Abstand
    peak_pressures = raw_pressure[peaks]
    peak_amps = envelope[peaks]
    # nach Druck sortieren (für Inflation von niedrig nach hoch)
    order = np.argsort(peak_pressures)
    return peak_pressures[order], peak_amps[order]

# 5) Schätzung von MAP und SYS
def estimate_sys_map(pressures, amplitudes, noise_factor=0.3):
    # MAP = Druck bei maximaler Amplitude
    idx_max = np.argmax(amplitudes)
    map_val = pressures[idx_max]

    # SYS = höchster Druck, bei dem Amplitude > noise_threshold
    noise_level = np.median(amplitudes[:5])
    threshold = noise_level + noise_factor*(np.max(amplitudes) - noise_level)
    sys_candidates = pressures[amplitudes > threshold]
    sys_val = np.max(sys_candidates) if len(sys_candidates) > 0 else np.nan

    return sys_val, map_val

# 6) Bootstrap-Fehlerabschätzung (für MAP)
def bootstrap_uncertainty(pressures, amplitudes, n_iter=200):
    map_vals = []
    N = len(pressures)
    for _ in range(n_iter):
        idx = np.random.choice(np.arange(N), size=N, replace=True)
        p_sample = pressures[idx]
        a_sample = amplitudes[idx]
        idx_max = np.argmax(a_sample)
        map_vals.append(p_sample[idx_max])
    return np.mean(map_vals), np.std(map_vals)

# 7) Visualisierung
def visualize_results(time, pressure, pressures, amplitudes, sys_val, map_val):
    plt.figure(figsize=(10,6))

    # Plot Rohsignal
    plt.subplot(2,1,1)
    plt.plot(time, pressure, label='Manschettendruck')
    plt.xlabel('Zeit (s)')
    plt.ylabel('Druck (mmHg)')
    plt.title('Manschettendruck über Zeit')
    plt.legend()

    # Plot Amplitude vs Druck
    plt.subplot(2,1,2)
    plt.scatter(pressures, amplitudes, s=10, label='Peak-Amplituden')
    plt.axvline(map_val, color='g', linestyle='--', label=f'MAP: {map_val:.1f} mmHg')
    plt.axvline(sys_val, color='r', linestyle='--', label=f'SYS: {sys_val:.1f} mmHg')
    plt.xlabel('Manschettendruck (mmHg)')
    plt.ylabel('Pulsamplitude')
    plt.title('Pulsamplitude vs. Manschettendruck')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Main Pipeline
def main():
    # Schritt 1: Laden
    t, cuff_p = load_data()

    # Schritt 2: Filtern
    sig_f = bandpass_filter(cuff_p)

    # Schritt 3: Envelope berechnen
    envelope = compute_envelope(sig_f)

    # Schritt 4: Peaks und Amplituden extrahieren
    peak_pressures, peak_amps = extract_peak_amplitudes(envelope, cuff_p)

    # Schritt 5: SYS und MAP schätzen
    sys_val, map_val = estimate_sys_map(peak_pressures, peak_amps)

    # Schritt 6: Bootstrap-Unsicherheit für MAP
    map_mean, map_std = bootstrap_uncertainty(peak_pressures, peak_amps)

    print(f"SYS geschätzt: {sys_val:.2f} mmHg")
    print(f"MAP geschätzt: {map_val:.2f} mmHg")
    print(f"MAP Bootstrap Mittelwert: {map_mean:.2f}, Std: {map_std:.2f}")

    # Schritt 7: Visualisierung
    visualize_results(t, cuff_p, peak_pressures, peak_amps, sys_val, map_val)

if __name__ == "__main__":
    main()

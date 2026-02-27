import json

import scipy.io
import numpy as np
from numpy import ndarray
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, savgol_filter

FILEPATH = "Messungen"
SAMPLING_FREQUENCY = 200
CUTOFF_FREQ = 0.5  # Grenzfrequenz, um die langsame Manschettendruckänderung zu entfernen


class Signal:
    def __init__(self, time, vCuffPressure):
        self.time: ndarray = time
        self.vCuffPressure:  ndarray = vCuffPressure
        self.envelope = None
        self.ramp = None
        self.oscillations = None

    def add_envelope(self, envelope):
        self.envelope = envelope


class Results:

    def __init__(self):
        self.map_pressure = None
        self.max_amplitude_index = None
        self.max_amplitude_value = None
        self.dia: float = None
        self.sys: float = None
        self.index_dia = None
        self.index_sys = None




def readDataIn() -> Signal:
    """
    Reads data from Measurement in
    :return: sample time and/with Cuff Pressure as ndarray
    """
    file_number = input("Welche Messung soll analysiert werden? -- ")
    data = scipy.io.loadmat(f"{FILEPATH}/{file_number}")

    if not isinstance(data, dict):
        raise Exception("The read in File has the wrong format")
    try:
        sample_time = data["vSampleTime"][0]
        sample_vCuffPressure = data["vCuffPressure"][0]
    except KeyError or IndexError:
        raise Exception("The read in File has the wrong format")

    #print(sample_time)
    #print(sample_vCuffPressure)

    return Signal(sample_time, sample_vCuffPressure)


# --- Schritt 1: Signalvorverarbeitung - Trennung von Rampe und Oszillationen ---
# Ziel ist es, das Rohsignal in zwei Komponenten zu zerlegen:
# 1. Die langsame Druckrampe (Tiefpassfilterung) -> Basis für Blutdruckwerte.
# 2. Die schnellen Oszillationen (Hochpassfilterung) -> Basis für die Hüllkurve.
# Dies entspricht konzeptionell Fig. 1b (Rohsignal), Fig. 1c (Oszillationen) und der impliziten Rampe.


def separate_signals(signal: Signal) -> Signal:
    """
        Trennt das Rohsignal in die langsame Rampe und die schnellen Oszillationen.
        Args:
            data (np.array): Das rohe Manschettendrucksignal.
            cutoff (float): Die Grenzfrequenz in Hz.
            fs (int): Die Abtastfrequenz.
        Returns:
            Aktualisiertes Signal
        """
    begin_index = np.where(signal.time == 3)[0]
    end_index = np.where(signal.vCuffPressure == np.max(signal.vCuffPressure))[0]
    processed_signal = Signal(
        time=signal.time[begin_index[0]:end_index[0]],
        vCuffPressure=signal.vCuffPressure[begin_index[0]:end_index[0]]
    )

    nyquist = 0.5 * SAMPLING_FREQUENCY
    normal_cutoff = CUTOFF_FREQ / nyquist

    # Hochpassfilter für die Oszillationen
    b_high, a_high = butter(4, normal_cutoff, btype='high', analog=False)
    oscillations = filtfilt(b_high, a_high, processed_signal.vCuffPressure)
    processed_signal.oscillations = oscillations

    # Tiefpassfilter für die Druckrampe
    b_low, a_low = butter(4, normal_cutoff, btype='low', analog=False)
    ramp = filtfilt(b_low, a_low, processed_signal.vCuffPressure)
    processed_signal.ramp = ramp

    return processed_signal


# --- Schritt 2: Erstellung der oszillometrischen Hüllkurve (Envelope) ---
# Die Amplitude der isolierten Oszillationen wird über die Zeit bestimmt.
# Das Ergebnis ist die sogenannte "amplitude oscillometric waveform", wie in Fig. 1d gezeigt[cite: 37, 66].
# Die Hilbert-Transformation ist eine robuste Methode, um die Hüllkurve eines Signals zu bestimmen.
def create_envelope(signal: Signal) -> Signal:
    # Die Hüllkurve wird mittels Hilbert-Transformation berechnet.
    analytic_signal = hilbert(signal.oscillations)
    envelope = np.abs(analytic_signal)

    # Glättung der Hüllkurve mittels eines Savitzky-Golay-Filters. Dies ist eine Polynom-Annäherung,
    # wie in der Aufgabenstellung gefordert, um Rauschen zu reduzieren und eine stabile Maximumsuche zu ermöglichen.
    # Das Paper arbeitet mit idealisierten Kurven[cite: 129], in der Praxis ist dieser Schritt entscheidend.

    # Glättung der Hüllkurve (Polynom-Annäherung)
    # Die Fensterlänge wird an die neue Abtastfrequenz angepasst (ca. 0.5 Sekunden Fenster).
    window_len = (SAMPLING_FREQUENCY // 4) * 2 + 1
    smoothed_envelope = savgol_filter(envelope, window_length=window_len, polyorder=3)
    signal.add_envelope(smoothed_envelope)
    return signal


def highpass_envelope(signal: Signal, k: float) -> Signal:
    """
    Wendet einen Hochpassfilter auf die Hüllkurve an.
    Args:
        signal: Das Signal-Objekt mit der bereits berechneten Envelope.
        k: Die Grenzfrequenz in Hz.
    Returns:
        Aktualisiertes Signal-Objekt.
    """
    if signal.envelope is None:
        raise ValueError("Envelope wurde noch nicht berechnet.")

    nyquist = 0.5 * SAMPLING_FREQUENCY
    # Normalisierung der Grenzfrequenz k
    normal_cutoff = k / nyquist

    # Definition des Hochpassfilters (Butterworth 4. Ordnung)
    b, a = butter(4, normal_cutoff, btype='high', analog=False)

    # Filterung anwenden
    filtered_envelope = filtfilt(b, a, signal.envelope)

    # Die Envelope im Objekt aktualisieren
    signal.envelope = filtered_envelope
    return signal


# --- Schritt 3: Anwendung des Maximum Amplitude Algorithmus (MAA) ---
# Der Manschettendruck am Punkt der maximalen Oszillationsamplitude
# wird als mittlerer arterieller Druck (MAP) geschätzt.
# Referenz: "The MAA estimate of the mean blood pressure is the occlusive cuff pressure at which the ...
# occlusive cuff pressure oscillation first reach their maximum amplitude".
def maximum_amplitude_algorithm(signal: Signal):
    max_amplitude_index = np.argmax(signal.envelope)
    max_amplitude_value = signal.envelope[max_amplitude_index]

    # Bestimmung des MAP aus dem ursprünglichen (langsamen) Manschettendrucksignal.
    map_pressure = signal.ramp[max_amplitude_index]
    raw_results = Results()
    raw_results.map_pressure = map_pressure
    raw_results.max_amplitude_value = max_amplitude_value
    raw_results.max_amplitude_index = max_amplitude_index
    return raw_results


# --- Schritt 4: Schätzung des systolischen und diastolischen Drucks ---
# Das Paper konzentriert sich auf den MAP. Die Bestimmung von systolischem (SBP) und
# diastolischem (DBP) Druck erfolgt in der Praxis oft durch feste Verhältnisse zur maximalen Amplitude.
# Diese Verhältnisse sind empirisch und nicht explizit im Paper definiert, aber das Prinzip,
# Merkmale der Wellenform zu nutzen, wird erwähnt.
#
# Annahme:
# - Diastolischer Druck (DBP): Bei ca. 75% der max. Amplitude auf der ansteigenden Flanke.
# - Systolischer Druck (SBP): Bei ca. 55% der max. Amplitude auf der abfallenden Flanke.
def predict_sys_and_dia(signal: Signal, raw_results: Results):
    # Schwellenwerte berechnen
    diastolic_threshold = 0.75 * raw_results.max_amplitude_value
    systolic_threshold = 0.55 * raw_results.max_amplitude_value

    # Suche nach dem diastolischen Punkt (ansteigende Flanke)
    rising_edge = signal.envelope[:raw_results.max_amplitude_index]
    # Finde den Index, an dem die ansteigende Flanke dem Schwellenwert am nächsten kommt.
    diastolic_index = np.argmin(np.abs(rising_edge - diastolic_threshold))
    diastolic_pressure = signal.ramp[diastolic_index]

    # Suche nach dem systolischen Punkt (abfallende Flanke)
    falling_edge = signal.envelope[raw_results.max_amplitude_index:]
    # Finde den Index, an dem die abfallende Flanke dem Schwellenwert am nächsten kommt.
    systolic_index_relative = np.argmin(np.abs(falling_edge - systolic_threshold))
    systolic_index = raw_results.max_amplitude_index + systolic_index_relative
    systolic_pressure = signal.ramp[systolic_index]
    results = raw_results
    results.sys = systolic_pressure
    results.dia = diastolic_pressure
    results.index_dia = diastolic_index
    results.index_sys = systolic_index
    return results


# --- Schritt 5: Ergebnisse und Visualisierung ---

def visualize(signal: Signal, results: Results):
    print("--- Ergebnisse der oszillometrischen Messung ---")
    print(f"Mittlerer Arterieller Druck (MAP): {results.map_pressure:.2f} mmHg")
    print(f"Systolischer Blutdruck (SBP):      {results.sys:.2f} mmHg")
    print(f"Diastolischer Blutdruck (DBP):    {results.dia:.2f} mmHg")

    # Plot erstellen
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Plot 1: Rohsignal und extrahierte Rampe
    color = 'tab:blue'
    ax1.set_xlabel('Zeit (s)')
    ax1.set_ylabel('Druck (mmHg)', color=color)
    ax1.plot(signal.time, signal.vCuffPressure, label='Rohes Manschettensignal (vCuffPressure)', color=color, alpha=0.4)
    ax1.plot(signal.time, signal.ramp, label='Gefilterte Druckrampe', color='black', linestyle='--')
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot 2: Oszillometrische Hüllkurve
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Oszillationsamplitude', color=color)
    ax2.plot(signal.time, signal.envelope, label='Geglättete Hüllkurve (Envelope)', color=color, linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    # Markierungen für SBP, DBP und MAP
    # MAP

    ax2.plot(signal.time[results.max_amplitude_index], results.max_amplitude_value, 'ko', markersize=8)
    ax1.annotate(f'MAP: {results.map_pressure:.1f} mmHg',
                 xy=(signal.time[results.max_amplitude_index], results.map_pressure),
                 xytext=(signal.time[results.max_amplitude_index] + 1, results.map_pressure + 15),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="k", lw=1, alpha=0.8))

    # SBP
    ax2.plot(signal.time[results.index_sys], signal.envelope[results.index_sys], 'go', markersize=8)
    ax1.annotate(f'SBP: {results.sys:.1f} mmHg',
                 xy=(signal.time[results.index_sys], results.sys),
                 xytext=(signal.time[results.index_sys] + 1, results.sys + 10),
                 arrowprops=dict(facecolor='green', shrink=0.05),
                 bbox=dict(boxstyle="round,pad=0.3", fc="lightgreen", ec="k", lw=1, alpha=0.8))

    # DBP
    
    ax2.plot(signal.time[results.index_dia], signal.envelope[results.index_dia], 'bo', markersize=8)
    ax1.annotate(f'DBP: {results.dia:.1f} mmHg',
                 xy=(signal.time[results.index_dia], results.dia),
                 xytext=(signal.time[results.index_dia] - 7, results.dia - 10),
                 arrowprops=dict(facecolor='blue', shrink=0.05),
                 bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="k", lw=1, alpha=0.8))

    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(0.95, 0.95))
    plt.title('Oszillometrische Blutdruckbestimmung aus Messdaten')
    plt.show()


if __name__ == "__main__":
    signal = readDataIn()
    """with open("daten.json", "w", encoding="utf-8") as f:
        json.dump({
            "Time": signal.time.tolist(),
            "vCuffPressure": signal.vCuffPressure.tolist(),
        }, f, indent=4, ensure_ascii=False)"""
    processed_signal = separate_signals(signal)
    processed_signal = create_envelope(processed_signal)
    k = 1/15  # Beispielwert für die Grenzfrequenz in Hz
    processed_signal = highpass_envelope(processed_signal, k)
    raw_results = maximum_amplitude_algorithm(processed_signal)
    results = predict_sys_and_dia(processed_signal, raw_results)
    visualize(processed_signal, results)



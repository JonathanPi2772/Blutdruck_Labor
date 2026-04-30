import os
import scipy.io
import numpy as np
from numpy import ndarray
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, sosfilt, filtfilt, find_peaks


class Signal:
    SAMPLING_FREQUENCY = 200 # Hz
    def __init__(self, sample_time: ndarray, sample_vCuffPressure: ndarray):
        self.time = sample_time
        self.vCuffPressure = sample_vCuffPressure
        self.oscillations = None
        self.ramp = None
        self.envelope = None
        self.smoothed_envelope = None
        #
        self.diastolic_pressure = None
        self.diastolic_index = None
        self.systolic_pressure = None
        self.systolic_index = None
        self.map_index = None
        self.map_time = None
        self.map_pressure = None

    def extracting_ramp(self, begin_index: int = 3, high_N: int = 8, low_N: int = 8, border_f: float = 1.0, use_absolute_value: bool = True):
        begin_index = np.where(self.time == begin_index)[0] # After x Seconds
        if len(begin_index) == 0:
            raise Exception("Begin Index not found")
        # Till the highest point, should be 190
        end_index = np.where(self.vCuffPressure == np.max(self.vCuffPressure))[0]
        processed_signal = Signal(
            sample_time=self.time[begin_index[0]:end_index[0]],
            sample_vCuffPressure=self.vCuffPressure[begin_index[0]:end_index[0]]
        )
        # Herzschlähe extrahieren. Frequenz so bei 70-160 Schlägen pro Minute
        # Zwischen 7/6 Hz und 16/6
        # Alles unter 1 Hz kann entfernt/gesplittet werden. Das wäre der langsame Druckanstieg
        # Nutzung eines Hochpassfilters

        # Koeffizienten des Filter
        coff_b, coff_a = butter(N=high_N, Wn=border_f, btype="high", analog=False, fs=self.SAMPLING_FREQUENCY, output="ba")
        # Filtfilt ist für med. Daten am besten. Es spiegelt an den Enden und filtert von beiden Seiten.
        # Dadurch gibt es keine Artefakte am Anfang
        processed_signal.oscillations = filtfilt(b=coff_b, a=coff_a, x=processed_signal.vCuffPressure)
        if use_absolute_value:
            processed_signal.oscillations = np.abs(processed_signal.oscillations)

        # Nun das was unter einem Herz ist ist der Anstieg des Drucks. Das braucht man später zur Berechnung
        coff_b, coff_a  = butter(N=low_N, Wn=border_f, btype="low", analog=False, fs=self.SAMPLING_FREQUENCY, output="ba")
        processed_signal.ramp = filtfilt(b=coff_b, a=coff_a,  x=processed_signal.vCuffPressure)
        return processed_signal

    def get_hüllenfunktion(self, peaks_distance:int=116, window_size:float=3.0):
        if self.ramp is not None and self.oscillations is not None:
            # Erstmal Peaks finden mit dem Abstand von geringen 70 Schlägen pro Minute, Puffer von 0.6
            # (7/6)*0.5*self.SAMPLING_FREQUENCY = 116
            peaks, _ = find_peaks(x=self.oscillations, distance=peaks_distance)
            # Interpolation zwischen den Peaks
            interp_func = interp1d(peaks, self.oscillations[peaks], kind='cubic', fill_value="extrapolate")
            # Hüllenkurve über das ganze Zeitsignal
            self.envelope = interp_func(np.arange(len(self.oscillations)))
            # Smooth mit Window Size von x Sekunden
            window = int(window_size * self.SAMPLING_FREQUENCY)
            self.smoothed_envelope = np.convolve(self.envelope, np.ones(window)/window, mode='same')
        else:
            raise Exception("Ramp is not available, Do this only with preprocessed signal")

    def get_blutdruckwerte(self, dia_treshhold: float = 0.55, sys_trashhold: float = 0.75) -> tuple[float, float]:
        self.map_index = np.argmax(self.smoothed_envelope)
        self.map_time = self.time[self.map_index]
        map_relative_pressure = self.smoothed_envelope[self.map_index]
        self.map_pressure = self.vCuffPressure[self.map_index]

        # Dia
        rising_edge = np.zeros_like(self.smoothed_envelope)
        rising_edge[:self.map_index] = self.smoothed_envelope[:self.map_index]
        self.diastolic_index = np.argmin(np.abs(rising_edge - (map_relative_pressure * dia_treshhold)))
        self.diastolic_pressure = self.ramp[self.diastolic_index]

        #Systolic
        falling_edge = np.zeros_like(self.smoothed_envelope)
        falling_edge[self.map_index:] = self.smoothed_envelope[self.map_index:]
        self.systolic_index = np.argmin(np.abs(falling_edge - (map_relative_pressure * sys_trashhold)))
        self.systolic_pressure = self.ramp[self.systolic_index]



    def plot_data(self, title: str = "Signal", filename: str = "Signal", save_plot: bool = False):
        fig, ax1 = plt.subplots()
        ax1.set_title(title)
        ax1.plot(self.time, self.vCuffPressure, color="blue", label="Raw Data")
        ax1.set_xlabel("Sample Time")
        ax1.set_ylabel("Cuff Pressure", color="blue")
        if self.ramp is not None:
            ax1.plot(self.time, self.ramp, color="green", label="Ramp")
        ax1.tick_params(axis='y', labelcolor="blue")
        if self.oscillations is not None:
            ax2 = ax1.twinx()
            ax2.set_ylabel('Oscillations', color="red")
            ax2.plot(self.time, self.oscillations, color="red", label="Oscillations")
            if self.envelope is not None:
                ax2.plot(self.time, self.envelope, color="orange", label="Envelope")
                ax2.plot(self.time, self.smoothed_envelope, color="black", label="Smoothed Envelope")
            ax2.tick_params(axis='y', labelcolor="red")

        if self.map_pressure is not None:
            ax2.plot(self.map_time, self.smoothed_envelope[self.map_index], 'ko', markersize=8, label="MAP")
            """ax1.annotate(f'MAP: {self.map_pressure:.1f} mmHg',
                         xy=(self.map_time, self.map_pressure),
                         xytext=(self.map_time + 1, self.map_pressure + 15),
                         arrowprops=dict(facecolor='black', shrink=0.05),
                         bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="k", lw=1, alpha=0.8))"""

            ax2.plot(self.time[self.systolic_index], self.smoothed_envelope[self.systolic_index], 'go', markersize=8)
            """ax1.annotate(f'Systolic: {self.systolic_pressure:.1f} mmHg',
                         xy=(self.time[self.systolic_index], self.systolic_pressure),
                         xytext=(self.time[self.systolic_index] + 1, self.systolic_pressure + 15),
                         arrowprops=dict(facecolor='green', shrink=0.05),
                         bbox=dict(boxstyle="round,pad=0.3", fc="lightgreen", ec="k", lw=1, alpha=0.8))"""

            ax2.plot(self.time[self.diastolic_index], self.smoothed_envelope[self.diastolic_index], 'bo', markersize=8)
            """ax1.annotate(f'Diastolic: {self.diastolic_pressure:.1f} mmHg',
                         xy=(self.time[self.diastolic_index], self.diastolic_pressure),
                         xytext=(self.time[self.diastolic_index] + 1, self.diastolic_pressure + 15),
                         arrowprops=dict(facecolor='blue', shrink=0.05),
                         bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="k", lw=1, alpha=0.8))"""

        fig.tight_layout()
        if save_plot:
            if filename is None:
                filename = title
            fig.savefig(os.path.join("analyse_imgs", f"{filename}.png"), dpi=150)
        plt.show()


def load_data(file_name: str) -> tuple[ndarray, ndarray]:
    "Loads data from a MAT file and returns the sample time and the cuff pressure"
    file_path = os.path.join("Messungen", f"{file_name}.mat")
    data = scipy.io.loadmat(file_path)

    if not isinstance(data, dict):
        raise Exception("The read in File has the wrong format")
    try:
        sample_time: ndarray = data["vSampleTime"][0]
        sample_vCuffPressure: ndarray = data["vCuffPressure"][0]
        return sample_time, sample_vCuffPressure
    except KeyError or IndexError:
        raise Exception("The read in File has the wrong format")


def alogrithmus(messnummer: str, begin_index: int, high_N: int, low_N: int, border_f: float, use_absolute_value: bool,
                peaks_distance: int, window_size: float,
                dia_treshhold: float, sys_trashhold: float
) -> tuple[float, float, Signal]:
    sample_time, sample_vCuffPressure = load_data(messnummer)
    signal = Signal(sample_time, sample_vCuffPressure)
    processed_signal = signal.extracting_ramp(
        begin_index=begin_index,
        high_N=high_N,
        low_N=low_N,
        border_f=border_f,
        use_absolute_value=use_absolute_value
    )
    processed_signal.get_hüllenfunktion(
        peaks_distance=peaks_distance,
        window_size=window_size
    )
    processed_signal.get_blutdruckwerte(
        dia_treshhold=dia_treshhold,
        sys_trashhold=sys_trashhold
    )
    return processed_signal.systolic_pressure, processed_signal.diastolic_pressure, processed_signal





if __name__ == "__main__":
    filename = "P06_REST_01_191025"
    print(filename)
    sample_time, sample_vCuffPressure = load_data(filename)
    signal = Signal(sample_time, sample_vCuffPressure)
    # signal.plot_data()
    processed_signal = signal.extracting_ramp(
        begin_index=1,
        high_N=2,
        low_N=3,
        border_f=1.648475101296686,
        use_absolute_value=False
    )
    processed_signal.get_hüllenfunktion(
        peaks_distance=154,
        window_size=2.291477696530879
    )
    processed_signal.get_blutdruckwerte(
        dia_treshhold=0.7482381534642903,
        sys_trashhold=0.8618229257116254
    )
    processed_signal.plot_data(title="P06_REST_01_191025", save_plot=True)
    print(f"Diastolic Pressure: {processed_signal.diastolic_pressure} mmHg\n"
          f"Systolic Pressure: {processed_signal.systolic_pressure} mmHg\n"
          f"MAP: {processed_signal.map_pressure} mmHg\n")


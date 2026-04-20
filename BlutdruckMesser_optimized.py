import os
import scipy.io
import numpy as np
from numpy import ndarray
from scipy.interpolate import pchip_interpolate
from scipy.signal import butter, sosfilt, filtfilt, find_peaks
import plotly.graph_objects as go

class Signal:
    SAMPLING_FREQUENCY = 200 # Hz
    def __init__(self, sample_time: ndarray, sample_vCuffPressure: ndarray):
        self.time = sample_time
        self.vCuffPressure = sample_vCuffPressure
        self.oscillations = None
        self.ramp = None
        self.envelope = None
        self.smoothed_envelope = None
        
        self.diastolic_pressure = None
        self.diastolic_index = None
        self.systolic_pressure = None
        self.systolic_index = None
        self.map_index = None
        self.map_time = None
        self.map_pressure = None

    def extracting_ramp(self, begin_index: int = 1, high_N: int = 3, low_N: int = 3, border_f: float = 1.0):
        # Begrenzung der Filterordnung auf max 4 für Stabilität
        high_N = max(1, min(high_N, 4))
        low_N = max(1, min(low_N, 4))
        
        begin_indices = np.where(self.time >= begin_index)[0]
        if len(begin_indices) == 0:
            raise Exception("Begin Index not found")
        
        # Inflation endet beim maximalen Manschettendruck
        end_index = np.argmax(self.vCuffPressure)
        
        processed_signal = Signal(
            sample_time=self.time[begin_indices[0]:end_index],
            sample_vCuffPressure=self.vCuffPressure[begin_indices[0]:end_index]
        )

        # Hochpassfilter für Oszillationen
        coff_b, coff_a = butter(N=high_N, Wn=border_f, btype="high", analog=False, fs=self.SAMPLING_FREQUENCY, output="ba")
        processed_signal.oscillations = filtfilt(b=coff_b, a=coff_a, x=processed_signal.vCuffPressure)

        # Tiefpassfilter für die Druck-Rampe
        coff_b, coff_a  = butter(N=low_N, Wn=border_f, btype="low", analog=False, fs=self.SAMPLING_FREQUENCY, output="ba")
        processed_signal.ramp = filtfilt(b=coff_b, a=coff_a,  x=processed_signal.vCuffPressure)
        return processed_signal

    def get_hüllenfunktion(self, peaks_distance: int = 150, window_size: float = 1.5):
        if self.ramp is not None and self.oscillations is not None:
            # Nutze die rohen Oszillationen für Maxima (keine Frequenzverdopplung durch abs())
            peaks, _ = find_peaks(x=self.oscillations, distance=peaks_distance)
            
            if len(peaks) < 3:
                # Fallback auf Absolutwert nur wenn nötig
                peaks, _ = find_peaks(x=np.abs(self.oscillations), distance=peaks_distance//2)

            # Pchip erzeugt keine künstlichen schwingungen zwischen den Stützstellen
            x_range = np.arange(len(self.oscillations))
            self.envelope = pchip_interpolate(peaks, self.oscillations[peaks], x_range)
            
            # Glättung mit Fensterbreite in Sekunden (physiologisch sinnvoll 1-2s)
            window = int(window_size * self.SAMPLING_FREQUENCY)
            if window % 2 == 0: window += 1
            self.smoothed_envelope = np.convolve(self.envelope, np.ones(window)/window, mode='same')
        else:
            raise Exception("Ramp not available")

    def get_blutdruckwerte(self, dia_treshhold: float = 0.6, sys_trashhold: float = 0.7):
        # MAP ist das Maximum der geglätteten Hüllkurve
        self.map_index = np.argmax(self.smoothed_envelope)
        self.map_time = self.time[self.map_index]
        map_max_amp = self.smoothed_envelope[self.map_index]
        self.map_pressure = self.ramp[self.map_index]

        # Inflation: Diastole liegt zeitlich VOR MAP (bei niedrigerem Manschettendruck)
        rising_edge = self.smoothed_envelope[:self.map_index]
        if len(rising_edge) > 0:
            self.diastolic_index = np.argmin(np.abs(rising_edge - (map_max_amp * dia_treshhold)))
            self.diastolic_pressure = self.ramp[self.diastolic_index]
        else:
            self.diastolic_pressure = 0

        # Inflation: Systole liegt zeitlich NACH MAP (bei höherem Manschettendruck)
        falling_edge = self.smoothed_envelope[self.map_index:]
        if len(falling_edge) > 0:
            self.systolic_index = self.map_index + np.argmin(np.abs(falling_edge - (map_max_amp * sys_trashhold)))
            self.systolic_pressure = self.ramp[self.systolic_index]
        else:
            self.systolic_pressure = 0

    def plot_data(self, title: str = "Signal", filename: str = "Signal", save_plot: bool = False, ref_sys: float = None, ref_dia: float = None):
        fig = go.Figure()

        # Cuff Pressure (Ramp & Raw)
        fig.add_trace(go.Scatter(x=self.time, y=self.vCuffPressure, name="Raw Data", line=dict(color='green', width=2), opacity=0.5))
        # fig.add_trace(go.Scatter(x=self.time, y=self.ramp, name="Ramp (Cuff Pressure)", line=dict(color='grey', width=2)))

        # Oscillations & Envelope (Secondary Y-Axis)
        fig.add_trace(go.Scatter(x=self.time, y=self.oscillations, name="Oscillations", line=dict(color='red', width=2), opacity=0.3, yaxis="y2"))
        fig.add_trace(go.Scatter(x=self.time, y=self.smoothed_envelope, name="Smoothed Envelope", line=dict(color='black', width=1), yaxis="y2"))

        # Calculated Values
        if self.map_pressure:
            # MAP
            fig.add_trace(go.Scatter(x=[self.map_time], y=[self.map_pressure], mode='markers+text', 
                                     name="Calculated MAP", text=[f"MAP: {self.map_pressure:.1f}"],
                                     textposition="top center", marker=dict(color='red', size=12, symbol='circle')))
            
            # Diastole
            dia_time = self.time[self.diastolic_index]
            fig.add_trace(go.Scatter(x=[dia_time], y=[self.diastolic_pressure], mode='markers+text', 
                                     name="Calculated Dia", text=[f"Dia: {self.diastolic_pressure:.1f}"],
                                     textposition="bottom center", marker=dict(color='blue', size=10, symbol='diamond')))
            fig.add_vline(x=dia_time, line=dict(color='blue', width=1, dash='dot'), opacity=0.5)

            # Systole
            sys_time = self.time[self.systolic_index]
            fig.add_trace(go.Scatter(x=[sys_time], y=[self.systolic_pressure], mode='markers+text', 
                                     name="Calculated Sys", text=[f"Sys: {self.systolic_pressure:.1f}"],
                                     textposition="top center", marker=dict(color='green', size=10, symbol='diamond')))
            fig.add_vline(x=sys_time, line=dict(color='green', width=1, dash='dot'), opacity=0.5)

        # Ground Truth (Reference)
        if ref_sys is not None:
            idx_sys = np.argmin(np.abs(self.ramp - ref_sys))
            ref_time_sys = self.time[idx_sys]
            fig.add_hline(y=ref_sys, line=dict(color='darkgreen', width=2, dash='dash'), annotation_text=f"Ref Sys: {ref_sys} mmHg")
            fig.add_vline(x=ref_time_sys, line=dict(color='darkgreen', width=1, dash='dash'))

        if ref_dia is not None:
            idx_dia = np.argmin(np.abs(self.ramp - ref_dia))
            ref_time_dia = self.time[idx_dia]
            fig.add_hline(y=ref_dia, line=dict(color='darkblue', width=2, dash='dash'), annotation_text=f"Ref Dia: {ref_dia} mmHg")
            fig.add_vline(x=ref_time_dia, line=dict(color='darkblue', width=1, dash='dash'))

        fig.update_layout(
            title=title,
            xaxis_title="Time [s]",
            yaxis_title="Pressure [mmHg]",
            yaxis2=dict(title="Amplitude", overlaying="y", side="right", showgrid=False),
            hovermode="x unified",
            template="plotly_white",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        if save_plot:
            # Note: Static export requires 'kaleido'
            pass
        
        fig.show()

def load_data(file_name: str):
    file_path = os.path.join("Messungen", f"{file_name}.mat")
    data = scipy.io.loadmat(file_path)
    return data["vSampleTime"][0], data["vCuffPressure"][0]

def alogrithmus_optimized(messnummer, begin_index, high_N, low_N, border_f, peaks_distance, window_size, dia_treshhold, sys_trashhold):
    time, press = load_data(messnummer)
    sig = Signal(time, press)
    proc = sig.extracting_ramp(begin_index, high_N, low_N, border_f)
    proc.get_hüllenfunktion(peaks_distance, window_size)
    proc.get_blutdruckwerte(dia_treshhold, sys_trashhold)
    return proc.systolic_pressure, proc.diastolic_pressure, proc

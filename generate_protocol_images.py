import os
import scipy.io
import numpy as np
import plotly.graph_objects as go
from BlutdruckMesser_optimized import alogrithmus_optimized as alogrithmus
from Messungen.Infos import MEASUREMENT_INFORMATION, COMBINED_BEST, BEURER_BEST, NAIS_BEST

def generate_all_plots():
    categories = [
        (COMBINED_BEST, "Combined", "combined"),
        (BEURER_BEST, "Beurer", "beurer"),
        (NAIS_BEST, "NAIS", "nais")
    ]
    
    if not os.path.exists("Protokoll/images"):
        os.makedirs("Protokoll/images")

    print(f"Generiere Messungs-Plots für {len(MEASUREMENT_INFORMATION)} Messungen in 3 Kategorien...")
    count = 0
    for messnummer, info in MEASUREMENT_INFORMATION.items():
        for params, label, suffix in categories:
            # Determine reference values for the plot
            b_sys, b_dia = info.get("Beurer", (None, None))
            n_sys, n_dia = info.get("NAIS", (None, None))
            
            ref_s, ref_d = None, None
            if suffix == "beurer":
                ref_s, ref_d = b_sys, b_dia
            elif suffix == "nais":
                ref_s, ref_d = n_sys, n_dia
            else: # combined
                refs = [r for r in [b_sys, n_sys] if r is not None]
                refd = [r for r in [b_dia, n_dia] if r is not None]
                if refs: ref_s = np.mean(refs)
                if refd: ref_d = np.mean(refd)

            try:
                calc_sys, calc_dia, signal = alogrithmus(messnummer=messnummer, **params)
                filename = f"{messnummer}_{suffix}"
                title = f"Messung: {messnummer} (Optimiert für {label})"
                signal.plot_data(title=title, filename=filename, save_plot=True, ref_sys=ref_s, ref_dia=ref_d, messnummer=messnummer)
                count += 1
                if count % 10 == 0:
                    print(f"Progress: {count} Plots generiert...")
            except Exception as e:
                print(f"Fehler bei {messnummer} ({suffix}): {e}")

    # Generate extraction example for main text
    print("Generiere Extraktions-Beispiel für den Hauptteil...")
    ex_mess = "P01_REST_01_100825"
    ex_params, ex_label, ex_suffix = categories[0]
    b_sys, b_dia = MEASUREMENT_INFORMATION[ex_mess].get("Beurer", (None, None))
    n_sys, n_dia = MEASUREMENT_INFORMATION[ex_mess].get("NAIS", (None, None))
    ref_s = np.mean([b_sys, n_sys])
    ref_d = np.mean([b_dia, n_dia])
    _, _, ex_sig = alogrithmus(messnummer=ex_mess, **ex_params)
    ex_sig.plot_data(title=f"Beispiel: {ex_mess} (Combined)", filename="extraktion_beispiel", save_plot=True, ref_sys=ref_s, ref_dia=ref_d, messnummer=ex_mess)

    print("Generiere Bland-Altman Plots...")
    generate_bland_altman_plotly()

def generate_bland_altman_plotly():
    # Use Combined parameters for the main BA plot
    calc_sys_list, ref_sys_list = [], []
    calc_dia_list, ref_dia_list = [], []
    labels = []
    
    for messnummer, info in MEASUREMENT_INFORMATION.items():
        b_sys, b_dia = info.get("Beurer", (None, None))
        n_sys, n_dia = info.get("NAIS", (None, None))
        
        refs = [r for r in [b_sys, n_sys] if r is not None]
        refd = [r for r in [b_dia, n_dia] if r is not None]
        if not refs or not refd: continue
        r_sys, r_dia = np.mean(refs), np.mean(refd)
        
        try:
            c_sys, c_dia, _ = alogrithmus(messnummer=messnummer, **COMBINED_BEST)
            calc_sys_list.append(c_sys)
            ref_sys_list.append(r_sys)
            calc_dia_list.append(c_dia)
            ref_dia_list.append(r_dia)
            labels.append(messnummer)
        except:
            continue

    def plot_ba_plotly(calc, ref, lbls, title, filename):
        calc, ref = np.array(calc), np.array(ref)
        means = (calc + ref) / 2
        diffs = calc - ref
        bias = np.mean(diffs)
        sd = np.std(diffs, ddof=1)
        
        fig = go.Figure()
        
        color_map = {"P": "blue", "S": "orange"}
        point_colors = [color_map.get(l[0], "grey") for l in lbls]
        
        fig.add_trace(go.Scatter(
            x=means, y=diffs, mode='markers', name='Messungen',
            text=lbls,
            marker=dict(size=10, color=point_colors, opacity=0.7, line=dict(width=1, color='black'))
        ))
        
        fig.add_hline(y=bias, line_dash="solid", line_color="red", annotation_text=f"Bias: {bias:.2f}")
        fig.add_hline(y=bias + 1.96*sd, line_dash="dash", line_color="green", annotation_text=f"+1.96 SD: {bias + 1.96*sd:.2f}")
        fig.add_hline(y=bias - 1.96*sd, line_dash="dash", line_color="green", annotation_text=f"-1.96 SD: {bias - 1.96*sd:.2f}")
        
        fig.update_layout(
            title=title,
            xaxis_title="Mittelwert beider Methoden [mmHg]",
            yaxis_title="Differenz (Algo - Ref) [mmHg]",
            template="plotly_white"
        )
        fig.write_image(f"Protokoll/images/{filename}.png", engine="kaleido", scale=2)

    plot_ba_plotly(calc_sys_list, ref_sys_list, labels, "Bland-Altman: Systole (Kombinierte Optimierung)", "bland_altman_sys")
    plot_ba_plotly(calc_dia_list, ref_dia_list, labels, "Bland-Altman: Diastole (Kombinierte Optimierung)", "bland_altman_dia")

    # Beurer Specific BA
    calc_sys_b, ref_sys_b = [], []
    calc_dia_b, ref_dia_b = [], []
    labels_b = []
    for m, info in MEASUREMENT_INFORMATION.items():
        b_s, b_d = info.get("Beurer", (None, None))
        if b_s is None: continue
        try:
            c_s, c_d, _ = alogrithmus(messnummer=m, **BEURER_BEST)
            calc_sys_b.append(c_s); ref_sys_b.append(b_s)
            calc_dia_b.append(c_d); ref_dia_b.append(b_d)
            labels_b.append(m)
        except: continue
    plot_ba_plotly(calc_sys_b, ref_sys_b, labels_b, "Bland-Altman: Systole (Beurer Optimierung)", "bland_altman_beurer_sys")
    plot_ba_plotly(calc_dia_b, ref_dia_b, labels_b, "Bland-Altman: Diastole (Beurer Optimierung)", "bland_altman_beurer_dia")

    # NAIS Specific BA
    calc_sys_n, ref_sys_n = [], []
    calc_dia_n, ref_dia_n = [], []
    labels_n = []
    for m, info in MEASUREMENT_INFORMATION.items():
        n_s, n_d = info.get("NAIS", (None, None))
        if n_s is None: continue
        try:
            c_s, c_d, _ = alogrithmus(messnummer=m, **NAIS_BEST)
            calc_sys_n.append(c_s); ref_sys_n.append(n_s)
            calc_dia_n.append(c_d); ref_dia_n.append(n_d)
            labels_n.append(m)
        except: continue
    plot_ba_plotly(calc_sys_n, ref_sys_n, labels_n, "Bland-Altman: Systole (NAIS Optimierung)", "bland_altman_nais_sys")
    plot_ba_plotly(calc_dia_n, ref_dia_n, labels_n, "Bland-Altman: Diastole (NAIS Optimierung)", "bland_altman_nais_dia")

if __name__ == "__main__":
    generate_all_plots()

import numpy as np
import os
from BlutdruckMesser import alogrithmus
from Messungen.Infos import MEASUREMENT_INFORMATION, COMBINED_BEST

def run_subgroup_analysis():
    """
    Berechnet Bias, MAE und SD getrennt für die Messreihen P (Eigene) und S (Hanna/Ziyi).
    Dies dient der Validierung der Robustheit des Algorithmus.
    """
    results = {
        "P": {"sys_diff": [], "dia_diff": []}, 
        "S": {"sys_diff": [], "dia_diff": []}
    }

    print("Starte Subgruppen-Analyse...")
    
    for messnummer, info in MEASUREMENT_INFORMATION.items():
        # Bestimme Gruppe anhand des Präfixes
        group = "P" if messnummer.startswith("P") else "S"
        
        # Referenzwerte (Mittelwert aus Beurer und NAIS falls vorhanden)
        b_sys, b_dia = info.get("Beurer", (None, None))
        n_sys, n_dia = info.get("NAIS", (None, None))
        
        refs = [r for r in [b_sys, n_sys] if r is not None]
        refd = [r for r in [b_dia, n_dia] if r is not None]
        
        if not refs or not refd:
            continue
            
        ref_sys, ref_dia = np.mean(refs), np.mean(refd)

        try:
            # Nutze die kombinierten Best-Parameter für den Vergleich
            calc_sys, calc_dia, _ = alogrithmus(messnummer, **COMBINED_BEST)
            results[group]["sys_diff"].append(calc_sys - ref_sys)
            results[group]["dia_diff"].append(calc_dia - ref_dia)
        except Exception as e:
            print(f"Fehler bei Messung {messnummer}: {e}")
            continue

    print("\n" + "="*50)
    print("ERGEBNISSE DER SUBGRUPPEN-ANALYSE")
    print("="*50)

    for group in ["P", "S"]:
        sys_diffs = np.array(results[group]["sys_diff"])
        dia_diffs = np.array(results[group]["dia_diff"])
        
        label = "Eigene Messungen (P)" if group == "P" else "Messungen Ziyi/Hanna (S)"
        
        print(f"\n>>> {label} (n={len(sys_diffs)})")
        print(f"Systole:")
        print(f"  Bias: {np.mean(sys_diffs):>6.2f} mmHg")
        print(f"  MAE:  {np.mean(np.abs(sys_diffs)):>6.2f} mmHg")
        print(f"  SD:   {np.std(sys_diffs):>6.2f} mmHg")
        
        print(f"Diastole:")
        print(f"  Bias: {np.mean(dia_diffs):>6.2f} mmHg")
        print(f"  MAE:  {np.mean(np.abs(dia_diffs)):>6.2f} mmHg")
        print(f"  SD:   {np.std(dia_diffs):>6.2f} mmHg")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    run_subgroup_analysis()

import json
import numpy as np
import optuna
from optuna.trial import Trial
from BlutdruckMesser_optimized import alogrithmus_optimized
from Messungen.Infos import MEASUREMENT_INFORMATION

ground_Truth = "NAIS"

def objective(trial: Trial):
    # Suchräume physiologisch begrenzt
    begin_index = trial.suggest_int("begin_index", 1, 3)
    high_N = trial.suggest_int("high_N", 2, 4)
    low_N = trial.suggest_int("low_N", 2, 4)
    border_f = trial.suggest_float("border_f", 0.6, 1.2)
    peaks_distance = trial.suggest_int("peaks_distance", 100, 250)
    
    # Begrenzte Fenstergröße gegen Signal-Verwässerung
    window_size = trial.suggest_float("window_size", 0.8, 2.5)
    
    # Klassische MAA Schwellwerte
    dia_treshhold = trial.suggest_float("dia_treshhold", 0.45, 0.85)
    sys_trashhold = trial.suggest_float("sys_trashhold", 0.45, 0.85)

    diffs_sys = []
    diffs_dia = []

    for messnummer, info in MEASUREMENT_INFORMATION.items():
        # Referenzwerte holen
        if ground_Truth == "COMBINED":
            n_sys, n_dia = info.get("NAIS", (None, None))
            b_sys, b_dia = info.get("Beurer", (None, None))
            refs = [r for r in [n_sys, b_sys] if r is not None]
            refd = [r for r in [n_dia, b_dia] if r is not None]
            if not refs or not refd: continue
            ref_sys, ref_dia = np.mean(refs), np.mean(refd)
        else:
            ref_sys, ref_dia = info.get(ground_Truth, (None, None))
        
        if ref_sys is None: continue

        try:
            calc_sys, calc_dia, sig = alogrithmus_optimized(
                messnummer, begin_index, high_N, low_N, border_f, 
                peaks_distance, window_size, dia_treshhold, sys_trashhold
            )
            
            # Plausibilitäts-Check Strafe
            if not (calc_dia < sig.map_pressure < calc_sys):
                diffs_sys.append(100)
                diffs_dia.append(100)
            else:
                diffs_sys.append(calc_sys - ref_sys)
                diffs_dia.append(calc_dia - ref_dia)
        except:
            return 1e6

    if not diffs_sys: return 1e6

    mae = np.mean(np.abs(diffs_sys)) + np.mean(np.abs(diffs_dia))
    sd = np.std(diffs_sys) + np.std(diffs_dia)
    
    # Konsistenz (SD) wird stärker gewichtet
    return mae + 2.0 * sd

def save_best(study, trial):
    if study.best_trial.number == trial.number:
        with open(f"Parameters/{ground_Truth}_optimized_params.json", "w") as f:
            json.dump(study.best_params, f, indent=4)

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=1000, callbacks=[save_best])

print(f"Optimierung abgeschlossen. Beste Parameter: {study.best_params}")

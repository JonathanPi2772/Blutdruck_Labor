import json
import numpy as np
import optuna
from optuna.trial import Trial

from BlutdruckMesser import alogrithmus
from Messungen.Infos import MEASUREMENT_INFORMATION

ground_Truth: str = "Beurer"
run: str = "2"

def objective(trial: Trial):
    begin_index = trial.suggest_int("begin_index", 1, 5)
    high_N = trial.suggest_int("high_N", 1, 10)
    low_N = trial.suggest_int("low_N", 1, 10)

    border_f = trial.suggest_float("border_f", 0.5, 1.2)
    use_absolute_value = trial.suggest_categorical("use_absolute_value", [True, False])
    peaks_distance = trial.suggest_int("peaks_distance", 50, 200)

    window_size = trial.suggest_float("window_size", 1, 8)
    dia_treshhold = trial.suggest_float("dia_treshhold", 0.4, 0.99)
    sys_trashhold = trial.suggest_float("sys_trashhold", 0.4, 0.99)

    # Anstatt den Fehler aufzuaddieren, sammeln wir die Abweichungen in Listen
    diffs_sys = []
    diffs_dia = []

    for key, value in MEASUREMENT_INFORMATION.items():
        messnummer = key
        sys, dia = (None, None)

        if ground_Truth == "Beurer":
            sys, dia = value.get("Beurer", (None, None))
        elif ground_Truth == "NAIS":
            sys, dia = value.get("NAIS", (None, None))
        elif ground_Truth == "COMBINED":
            n_sys, n_dia = value.get("NAIS", (None, None))
            b_sys, b_dia = value.get("Beurer", (None, None))

            if b_sys is None or b_dia is None:
                sys, dia = (n_sys, n_dia)
            elif n_sys is None or n_dia is None:
                sys, dia = (b_sys, b_dia)
            else:
                sys = (float(n_sys) + float(b_sys)) / 2
                dia = (float(n_dia) + float(b_dia)) / 2

        if sys is None or dia is None:
            continue

        try:
            calc_sys, calc_dia, _ = alogrithmus(
                messnummer=messnummer,
                begin_index=begin_index,
                high_N=high_N,
                low_N=low_N,
                border_f=border_f,
                use_absolute_value=use_absolute_value,
                peaks_distance=peaks_distance,
                window_size=window_size,
                dia_treshhold=dia_treshhold,
                sys_trashhold=sys_trashhold
            )

            # Echte Differenz (mit Vorzeichen) speichern für SD-Berechnung
            diffs_sys.append(calc_sys - float(sys))
            diffs_dia.append(calc_dia - float(dia))

        except Exception:
            # Bei Algorithmus-Absturz: Sehr hohe Strafe
            return 100000.0

    # Wenn keine gültigen Messungen zustande kamen
    if len(diffs_sys) == 0:
        return 100000.0

    # --- CUSTOM LOSS FUNCTION ---

    # 1. Mean Absolute Error (Wie weit sind wir im Schnitt weg?)
    mae_sys = np.mean(np.abs(diffs_sys))
    mae_dia = np.mean(np.abs(diffs_dia))

    # 2. Standardabweichung (Wie stark streuen die Fehler?)
    sd_sys = np.std(diffs_sys, ddof=1) if len(diffs_sys) > 1 else 0
    sd_dia = np.std(diffs_dia, ddof=1) if len(diffs_dia) > 1 else 0

    # 3. Der Loss: Wir bestrafen die Streuung doppelt so stark wie den reinen Fehler
    # Formel: Loss = MAE + (2 * SD)
    penalty_weight = 2.0
    loss = (mae_sys + mae_dia) + penalty_weight * (sd_sys + sd_dia)

    return loss


# --- Callback-Funktion zum Speichern ---
def save_best_callback(study, trial):
    # Wenn der aktuelle Trial der bisher beste ist, speichere ihn ab
    if study.best_trial.number == trial.number:
        with open(f"Parameters/{ground_Truth}{run}_beste_parameter.json", "w") as f:
            json.dump(study.best_params, f, indent=4)
        print(f"--> Neue beste Parameter in '{ground_Truth}_beste_parameter.json' gespeichert (Loss: {trial.value:.2f})")


# --- Optimierung starten ---
study = optuna.create_study(direction="minimize")

initial_params = {
    "begin_index": 3,
    "high_N": 4,
    "low_N": 4,
    "border_f": 1,
    "use_absolute_value": True,
    "peaks_distance": 116,
    "window_size": 3.0,
    "dia_treshhold": 0.55,
    "sys_trashhold": 0.75
}

study.enqueue_trial(initial_params)
study.optimize(objective, n_trials=1000, callbacks=[save_best_callback])

print(f"\nFertig! All-Time Beste Parameter: {study.best_params}")



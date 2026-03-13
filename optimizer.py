import optuna
from optuna.trial import Trial

from BlutdruckMesser import alogrithmus
from Messungen.Infos import MEASUREMENT_INFORMATION

def objective(trial: Trial, ground_Truth: str = "COMBINED"):
    begin_index = trial.suggest_int("begin_index", 1, 10)
    high_N = trial.suggest_int("high_N", 1, 10)
    low_N =  trial.suggest_int("low_N", 1, 10)

    border_f = trial.suggest_float("border_f", 0.25, 3)
    use_absolute_value= trial.suggest_categorical("use_absolute_value", [True, False])
    peaks_distance = trial.suggest_int("peaks_distance", 10, 250)

    window_size = trial.suggest_float("window_size", 0.1, 8)
    dia_treshhold = trial.suggest_float("dia_treshhold", 0.1, 0.99)
    sys_trashhold = trial.suggest_float("sys_trashhold", 0.1, 0.99)

    error = 0
    iterations = 0

    for key, value in MEASUREMENT_INFORMATION.items():

        messnummer = key
        sys, dia = (None, None)
        if ground_Truth == "Beurer":
            sys, dia = value["Beurer"]

        elif ground_Truth == "NAIS":
            sys, dia = value["NAIS"]

        elif ground_Truth == "COMBINED":
            n_sys, n_dia = value["NAIS"]
            b_sys, b_dia = value["Beurer"]
            if b_sys is None or b_dia is None:
                sys, dia = value["NAIS"]
            elif n_sys is None or n_dia is None:
                sys, dia = value["Beurer"]
            else:
                sys = (n_sys + b_sys)/2
                dia = (n_dia + b_dia)/2

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
            error += (calc_sys - sys)**2 + (calc_dia - dia)**2
            iterations += 1
        except Exception as e:
            return 100000.0

    error /= (iterations*2)
    return error

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=1000)

print(f"Beste Parameter: {study.best_params}")



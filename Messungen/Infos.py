MEASUREMENT_INFORMATION: dict = {
    "P01_REST_01_100825": {
        "Beurer": (104, 62),
        "NAIS": (97, 60),
    },
    "P01_REST_02_100825": {
        "Beurer": (98, 57),
        "NAIS": (106, 55),
    },
    "P01_ACTIV_01_160925": {
        "Beurer": (147, 81),
        "NAIS": (128, 78),
    },
    # ---
    "P02_REST_01_100825": {
        "Beurer": (111, 70),
        "NAIS": (None, None),
    },
    "P02_REST_02_160925": {
        "Beurer": (113, 66),
        "NAIS": (116, 75),
    },
    "P02_ACTIV_01_160925": {
        "Beurer": (134, 77),
        "NAIS": (127, 75),
    },
    # ---
    "P03_REST_01_100825": {
        "Beurer": (None, None),
        "NAIS": (109, 63),
    },
    "P03_REST_02_160925": {
        "Beurer": (100, 59),
        "NAIS": (112, 61),
    },
    "P03_ACTIV_02_160925": {
        "Beurer": (112, 61),
        "NAIS": (111, 67),
    },
    # ---
    "P04_REST_01_160925": {
        "Beurer": (101, 68),
        "NAIS": (114, 71),
    },
    "P04_ACTIV_01_160925": {
        "Beurer": (125, 70),
        "NAIS": (127, 77),
    },
    # #######################

    "P05_REST_01_210925": {
        "Beurer": (122, 68),
        "NAIS": (128, 64),
    },
    "P05_ACTIV_01_210925": {
        "Beurer": (137, 74),
        "NAIS": (160, 70),
    },
    # ---
    "P06_REST_01_191025": {
        "Beurer": (122, 86),
        "NAIS": (136, 87),
    },
    "P06_ACTIV_01_191025": {
        "Beurer": (141, 64),
        "NAIS": (156, 84),
    },
    # ---
    "P07_REST_01_191025": {
        "Beurer": (111, 70),
        "NAIS": (123, 77),
    },
    "P07_ACTIV_01_191025": {
        "Beurer": (150, 74),
        "NAIS": (145, 76),
    },
    # ---
    "P08_REST_01_201025": {
        "Beurer": (98, 63),
        "NAIS": (108, 69),
    },
    "P08_ACTIV_01_201025": {
        "Beurer": (124, 64),
        "NAIS": (124, 75),
    }
}


COMBINED_BEST = {
    "begin_index": 4,
    "high_N": 8,
    "low_N": 2,
    "border_f": 1.3618632141628064,
    "use_absolute_value": True,
    "peaks_distance": 130,
    "window_size": 5.6119152611238885,
    "dia_treshhold": 0.7255318911571096,
    "sys_trashhold": 0.8569972699918027
}

BEURER_BEST = {
    "begin_index": 3,
    "high_N": 2,
    "low_N": 6,
    "border_f": 1.1865534774567805,
    "use_absolute_value": True,
    "peaks_distance": 152,
    "window_size": 5.3634623241166235,
    "dia_treshhold": 0.6887613098188278,
    "sys_trashhold": 0.8397497178812133
}

NAIS_BEST = {
    "begin_index": 1,
    "high_N": 2,
    "low_N": 3,
    "border_f": 1.2993508025033014,
    "use_absolute_value": False,
    "peaks_distance": 176,
    "window_size": 3.7664897102734063,
    "dia_treshhold": 0.715214015918205,
    "sys_trashhold": 0.7684376006888789
}


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
    },

    # --- Hanna und Ziyi ---
    "S001-M001-Rest": {
        "Beurer": (103, 66),
        "NAIS": (None, None),
    },
    "S001-M002-Active": {
        "Beurer": (105, 73),
        "NAIS": (None, None),
    },

    # ---
    "S002-M001-Rest": {
        "Beurer": (169, 107),
        "NAIS": (155, 104),
    },
    "S002-M002-Active": {
        "Beurer": (152, 110),
        "NAIS": (170, 111),
    },

    # ---
    "S003-M001-Rest": {
        "Beurer": (107, 64),
        "NAIS": (111, 73),
    },
    "S003-M002-Active": {
        "Beurer": (110, 66),
        "NAIS": (115, 75),
    },

    # ---
    "S004-M001-Rest": {
        "Beurer": (131, 82),
        "NAIS": (122, 82),
    },
    "S004-M002-Active": {
        "Beurer": (126, 85),
        "NAIS": (122, 81),
    },

    # ---
    "S005-M001-Rest": {
        "Beurer": (129, 96),
        "NAIS": (147, 101),
    },
    "S005-M002-Active": {
        "Beurer": (146, 95),
        "NAIS": (148, 103),
    },

    # ---
    "S006-M001-Rest": {
        "Beurer": (134, 87),
        "NAIS": (133, 83),
    },
    "S006-M002-Active": {
        "Beurer": (125, 89),
        "NAIS": (159, 122),
    },

    # ---
    "S007-M001-Rest": {
        "Beurer": (134, 89),
        "NAIS": (165, 102),
    },
    "S007-M002-Active": {
        "Beurer": (149, 89),
        "NAIS": (180, 88),
    },

    # ---
    "S008-M001-Rest": {
        "Beurer": (137, 94),
        # "NAIS": (72, 61), # --- Eventuell ignorieren
        "NAIS": (None, None),
    },
    "S008-M002-Active": {
        "Beurer": (162, 129),
        "NAIS": (146, 99),
    },

    # ---
    "S009-M001-Rest": {
        "Beurer": (114, 81),
        "NAIS": (None, None),
    },
    "S009-M002-Active": {
        "Beurer": (115, 81),
        "NAIS": (132, 97),
    },

    # ---
    "S010-M001-Rest": {
        "Beurer": (108, 75),
        "NAIS": (127, 80),
    },
    "S010-M002-Active": {
        "Beurer": (124, 76),
        "NAIS": (132, 87),
    },

    # ---
    "S011-M001-Rest": {
        "Beurer": (133, 90),
        "NAIS": (139, 104),
    },
    "S011-M002-Active": {
        "Beurer": (144, 92),
        "NAIS": (150, 96),
    },

    # ---
    "S012-M001-Rest": {
        "Beurer": (136, 87),
        "NAIS": (128, 89),
    },
    "S012-M002-Active": {
        "Beurer": (140, 82),
        "NAIS": (139, 84),
    },

    # ---
    "S013-M001-Rest": {
        "Beurer": (89, 74),
        "NAIS": (None, None),
    },
    "S013-M002-Active": {
        "Beurer": (108, 74),
        "NAIS": (None, None),
    },
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


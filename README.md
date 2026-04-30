# V16 - Oszillometrische Blutdruckmessung (iOBP)

Dieses Repository enthält die Implementierung und Auswertung eines oszillometrischen Blutdruckmess-Algorithmus, der im Rahmen des Praktikums **Diagnose- und Therapiesysteme** entwickelt wurde.

## Projektübersicht

Das Ziel des Projekts ist die Extraktion von Blutdruckwerten (Systole, Diastole, MAP) aus oszillometrischen Drucksignalen, die während der Inflationsphase einer Blutdruckmanschette aufgenommen wurden.

### Kernfunktionen
*   **Signalverarbeitung:** Trennung der Druckrampe von den Oszillationen mittels Butterworth-Filtern (Hoch- und Tiefpass).
*   **Hüllkurvenextraktion:** Bestimmung der Oszillations-Amplitude durch PCHIP-Interpolation.
*   **Algorithmische Schätzung:** Implementierung des Maximum Amplitude Algorithm (MAA) mit optimierbaren Amplituden-Schwellenwerten.
*   **Optimierung:** Automatisierte Parameter-Suche (Schwellenwerte, Filterordnungen, Fenstergrößen) mittels Optuna.
*   **Validierung:** Statistische Auswertung über Bland-Altman-Plots.

## Ordnerstruktur

```text
.
├── Analysis.ipynb          # Haupt-Analyse-Notebook (Exploration & Visualisierung)
├── BlutdruckMesser.py      # Kernlogik des Algorithmus (Signal-Klasse)
├── optimizer.py            # Optuna-Skript zur Parameter-Optimierung
├── Messungen/              # Rohdaten (.mat) und Referenzwerte
├── Parameters/             # Optimierte Parameter-Sets (JSON)
├── Protokoll/              # LaTeX-Quellcode und generierte Grafiken
├── html_files/             # Exportierte HTML-Versionen der Analyse
└── Literatur/              # Wissenschaftliche Referenzdokumente
```

## Installation & Nutzung

1.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirments.txt
    ```

2.  **Analyse ausführen:**
    Öffne die `Analysis.ipynb` in Jupyter oder VS Code, um die vollständige Pipeline von der Rohdatenverarbeitung bis zu den Bland-Altman-Plots nachzuvollziehen.

3.  **Parameter optimieren:**
    Falls neue weitere Messungen vorliegen, kann der Optimizer gestartet werden:
    ```bash
    python optimizer.py
    ```

4.  **Subgruppen-Analyse:**
    Vergleich der Genauigkeit zwischen den verschiedenen Probandengruppen:
    ```bash
    python Protokoll/subgroup_analysis.py
    ```

## Ergebnisse

Die Ergebnisse befinden sich sowohl im Protokoll als auch in dem Analyse-Jupyter-Notebook.

## Autoren
*   **Bianca Kaiser**
*   **Jonathan Pareja Carrillo**

*Aufgabe V16 vom 30.04.2026 - Praktikum Diagnose- und Therapiesysteme*

from Messungen.Infos import MEASUREMENT_INFORMATION

def generate_appendix_latex():
    with open("Protokoll/appendix.tex", "w") as f:
        f.write("\\section*{Anhang: Einzelauswertungen}\n")
        f.write("In diesem Anhang sind die Einzelauswertungen für alle 23 Probanden unter Anwendung der drei verschiedenen Optimierungsszenarien dargestellt.\n\n")
        
        # Group by measurement
        for messnummer in sorted(MEASUREMENT_INFORMATION.keys()):
            f.write(f"\\subsection*{{Messung: {messnummer.replace('_', '\\_')}}}\n")
            
            # Subfigures for the 3 categories
            f.write("\\begin{figure}[H]\n")
            f.write("    \\centering\n")
            
            # Combined
            f.write("    \\begin{subfigure}[b]{0.8\\textwidth}\n")
            f.write(f"        \\includegraphics[width=\\textwidth]{{images/{messnummer}_combined.png}}\n")
            f.write(f"        \\caption{{Optimiert für Beurer und NAIS (Kombiniert)}}\n")
            f.write("    \\end{subfigure} \\\\\n")
            
            # Beurer
            f.write("    \\begin{subfigure}[b]{0.48\\textwidth}\n")
            f.write(f"        \\includegraphics[width=\\textwidth]{{images/{messnummer}_beurer.png}}\n")
            f.write(f"        \\caption{{Optimiert für Beurer}}\n")
            f.write("    \\end{subfigure}\n")
            f.write("    \\hfill\n")
            
            # NAIS
            f.write("    \\begin{subfigure}[b]{0.48\\textwidth}\n")
            f.write(f"        \\includegraphics[width=\\textwidth]{{images/{messnummer}_nais.png}}\n")
            f.write(f"        \\caption{{Optimiert für NAIS}}\n")
            f.write("    \\end{subfigure}\n")
            
            f.write(f"    \\caption{{Einzelauswertung der Messung {messnummer.replace('_', '\\_')} mit verschiedenen Parametersätzen.}}\n")
            f.write("\\end{figure}\n")
            f.write("\\newpage\n\n")

if __name__ == "__main__":
    generate_appendix_latex()

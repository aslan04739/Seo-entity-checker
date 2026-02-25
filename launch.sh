#!/bin/bash
# SEO Crawler Desktop Launcher for macOS

cd "$(dirname "$0")"
PYTHON_BIN=""

for candidate in ".venv/bin/python" ".venv-1/bin/python"; do
	if command -v "$candidate" >/dev/null 2>&1 || [ -x "$candidate" ]; then
		if ( "$candidate" -c "import customtkinter; import tkinter as tk; root = tk.Tk(); root.withdraw(); root.destroy()" ) >/dev/null 2>&1; then
			PYTHON_BIN="$candidate"
			break
		fi
	fi
done

if [ -z "$PYTHON_BIN" ]; then
	echo "Erreur: aucun Python compatible GUI n'a été trouvé."
	echo "Causes possibles:"
	echo "- customtkinter non installé"
	echo "- Python compilé sans tkinter (_tkinter manquant)"
	echo "- tkinter incompatible avec cette version de macOS"
	echo ""
	echo "Solution recommandée:"
	echo "1) Installer Python 3.12+ (python.org ou Homebrew) avec tkinter"
	echo "2) Recréer l'environnement virtuel"
	echo "3) Installer les dépendances: python -m pip install -r requirements.txt"
	echo ""
	echo "Alternative immédiate (sans GUI tkinter):"
	echo "streamlit run streamlit_app.py"
	exit 1
fi

"$PYTHON_BIN" analyze2.py &
disown

# CityProject

1. Define the building types in the building.csv
2. run the command python erzeuge_druckvorlagen.py --csv gebaeude.csv --out ausgabe to create the print outs for the grid and the buildings.

pip install -r requirements.txt
python scripts/generate_prints.py
python scripts/detect_city.py --image photo.jpg
godot --path cityviewer -- scanresult/city.json (& .\Godot_v4.7.2-stable_win64.exe --path cityviewer -- C:\Users\Joe\Documents\GitHub\city_project\scanresult\city.json)
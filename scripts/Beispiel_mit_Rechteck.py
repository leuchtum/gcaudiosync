# Hier wird die Klasse importiert
from scripts.Beispiel_Klasse_Rechteck import Rechteck

# Erstellen zweier Objekte der Klasse Rechteck
Rechteck_1 = Rechteck(Laenge=14, Breite=5, Farbe="gelb")
Rechteck_2 = Rechteck(Laenge=3, Breite=19, Farbe="blau")

# Man kann direkt auf die Attribute von Objekten zugreifen:
print(f"Rechteck 1 hat folgende Farbe: {Rechteck_1.Farbe}")
print(f"Rechteck 2 hat folgende Laenge: {Rechteck_2.Laenge}")

# Methoden werden auch so aufgerufen:
print(f"Rechteck 1 hat folgenden Flaecheninhalt: {Rechteck_1.Flaecheninhalt()}")
print(f"Rechteck 2 hat mit einer Hoehe von 10 das Volumen: {Rechteck_2.Volumen_Quarder(Hoehe=10)}")



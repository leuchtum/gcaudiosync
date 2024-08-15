class Rechteck:

    # Initialisierungmethode: Hier werden alle Attribute definiert.
    # Parameter sind das Key-Wort self und drei Übergabeparameter.
    # Bei den Parametern Laenge und Breite handelt es sich um Integer.
    # Bei dem Parameter Farbe handelt es sich um einen String.
    def __init__(self, Laenge: int, Breite: int, Farbe: str):
        
        # Hier werden die Attribute definiert.
        self.Laenge = Laenge
        self.Breite = Breite
        self.Farbe = Farbe

    # Methode zur Berechnung des Flächeninhalts. Keine Übergabeparameter notwendig.
    def Flaecheninhalt(self):
        # Mit dem Key-Wort self wird auf die eigenen Attribute verwiesen.
        return self.Laenge * self.Breite
    
    # Methode zur Berechnung des Volumens mit einem zusätzlichen Übergabeparameter.
    # Bei dem Parameter Hoehe handelt es sich um einen Integer.
    # Der Rückgabewert der Methode ist ebenso ein Integer.
    def Volumen_Quarder(self, Hoehe: int) -> int:

        # Anstatt self.Laenge * self.Breite * Hoehe zu rechnen, wird die Methode zur 
        # Berechnung des Flaecheninhalts aufgerufen. Da wir uns hier in der Klasse befinden
        # geschieht dies auch mit dem Key-Wort self

        return self.Flaecheninhalt() * Hoehe

    # Methode zur Ausgabe aller Attribute des Objekts. Keine Übergabeparameter notwendig.
    def Print_Info(self):
        print(f"Laenge = {self.Laenge} cm")
        print(f"Breite:     {self.Breite}")
        print(f"Farbe:        {self.Farbe}")




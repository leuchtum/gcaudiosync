# Schaltjahrrechner

# Hier wird die Funktion "Berechne_ob_Schaltjahr" definiert
# Die Funktion hat einen Übergabeparameter "Jahreszahl" (Integer)
# Die Funktion gibt einen bool zurück
def Berechne_ob_Schaltjahr(Jahreszahl: int) -> bool:

    if Jahreszahl % 400 == 0:       # Ist die Jahreszahl durch 400 restlos teilbar, so ist es ein Schaltjahr
        return True
    elif Jahreszahl % 100 == 0:     # Ist die Jahreszahl sonst durch 100 restlos teilbar, so ist es kein Schaltjahr
        return False
    elif Jahreszahl % 4 == 0:       # Ist die Jahreszahl sonst durch 4 restlos teilbar, so ist es ein Schaltjahr
        return True
    else:                           # Sonst ist die Jahreszahl kein Schaltjahr
        return False
    
# Hier startet das eigentliche Programm
while True:

    # Benutzer wird aufgefordert, eine Jahreszahl einzutippen.
    Jahreszahl = input("Geben Sie eine Jahreszahl ein und bestätigen Sie mit Enter. \n" + 
                       "Geben Sie etwas anderes ein, um das Programm zu beenden. \n")

    # Es wird überprüft, ob etwas eingegeben wurde.
    # Wurde keine Jahreszahl eingegeben, so wird das Programm beendet.
    if not Jahreszahl.isdigit():
        break

    # Wandle die Eingabe in einen Int um.
    Jahreszahl = int(Jahreszahl)

    # Funktionsaufruf um herauszufinden, ob das Jahr ein Schaltjahr ist.
    Schaltjahr = Berechne_ob_Schaltjahr(Jahreszahl = Jahreszahl)
    
    # Dem Nutzer wird ausgegeben, ob es sich um ein Schaltjahr handelt
    if Schaltjahr:
        print(f"{Jahreszahl} ist ein Schaltjahr.")
    else:
        print(f"{Jahreszahl} ist kein Schaltjahr.")

        
; Testfall 2
; Erkennung Start und Ende mit Snapshot
G17
G54
; Snapshot 1
G04 P500
M03 S66
G4 P3.
M5
;
G00 X0 Y0 Z0 S80 M3
G04 P11.5
;
; Snapshot 2
M5
G04 P500
M03 S66
G4 P3.
M5
;
M30
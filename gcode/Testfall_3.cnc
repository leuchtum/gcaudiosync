; Testfall 3
; Snapshoterkennung im Progamm
G17
G54
G00 X0 Y0 Z0 
M03 S80
G04 P11.5
G01 X100 F500
G01 Y100
G01 X0 Y0
;
; Snapshot 
M5
G04 P500
M03 S66
G4 P3.
M5
;
G01 X100
G01 Y100
G01 X0 Y0
;
M30
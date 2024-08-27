;Kreise mit Radiuskompensation
G54
G0 X0 Y0    ; Start here    
M03 S25
F500       ; feed
G0 X-10 Y90 ; start point of entry arc
/G42 D10    ; Tool comp right diameter is 10mm
G2 X0 Y100 I10 J0  ; Tool comp entry move
G2 X0 Y100 I0 J-100 ; Full circle tool compensated
G2 X10 Y90 I0 J-10  ; Exit move
/G40          ;Tool comp off
G0 x0 Y0     ;back to 0,0

S50
F1000       ; feed
G0 X-10 Y90 ; start point of entry arc
/G42 D10    ; Tool comp right diameter is 10mm
G2 X0 Y100 I10 J0  ; Tool comp entry move
G2 X0 Y100 I0 J-100 ; Full circle tool compensated
G2 X10 Y90 I0 J-10  ; Exit move
/G40          ;Tool comp off
G0 x0 Y0     ;back to 0,0

S75
F2500       ; feed
G0 X-10 Y90 ; start point of entry arc
/G42 D10    ; Tool comp right diameter is 10mm
G2 X0 Y100 I10 J0  ; Tool comp entry move
G2 X0 Y100 I0 J-100 ; Full circle tool compensated
G2 X10 Y90 I0 J-10  ; Exit move
/G40          ;Tool comp off
G0 x0 Y0     ;back to 0,0

S100
F5000       ; feed
G0 X-10 Y90 ; start point of entry arc
/G42 D10    ; Tool comp right diameter is 10mm
G2 X0 Y100 I10 J0  ; Tool comp entry move
G2 X0 Y100 I0 J-100 ; Full circle tool compensated
G2 X10 Y90 I0 J-10  ; Exit move
/G40          ;Tool comp off
G0 x0 Y0     ;back to 0,0
M05
M30





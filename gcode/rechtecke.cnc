; Rechteckefräsen
G17
G54
M3
g0 z3 S80
g0 x-15 y15
f500
/g42.1 D6
g1 x-5       (cutter comp entry move 1)
g2 x0 y10 r5 (cutter comp entry move 2)
g1 z-3       (plunge down)
g3 x10 y0 r10
g1 x70
g3 x80 y10 r10 F1000
g1 y90
g3 x70 y100 r10
g1 x10
g3 x0 y90 r10
g1 x0 y10
/g40
g0 z3 S90
g0 x30 y30
/g41.1 d6
g1 x20 F500
g3 x10 y20 r10
g1 z-3
g3 x20 y10 r10
g1 x70
g1 y90 F1000
g1 x10 F2500
g1 y10 F5000
g0 z3
m30
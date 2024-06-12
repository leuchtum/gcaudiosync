import numpy as np

# TODO: comment
def bisection_method(f, x0, x1, tol):

    if x0 >= x1:
        raise Exception(f"x0 must be smaller than x1")

    if f(x0)*f(x1) < 0 and x0<x1:
        
        f_0 = f(x0)

        while True:

            x_m = (x0 + x1) / 2.0
            f_m = f(x_m)

            if x1 - x0 <= tol or f_m == 0:
                return x_m
            
            elif f_0 * f_m < 0: 
                x1 = x_m
                
            else:
                x0 = x_m
                f_0 = f_m
    
    else:
        raise Exception(f"No zero falue in this interval found.")
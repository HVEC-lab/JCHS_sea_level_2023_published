"""
Empirical sea level models
"""

import numpy as np

T = np.array([8.85, 18.61])
omega = (2 * np.pi) / T


def model1(t, a, b):
    return b * t + a


def model2(t, a, b, c):
    return c * t**2 + b * t + a


def model3a(t, a, b, Ac, As):
    return (
        model1(t, a, b)
        + Ac * np.cos(omega[0] * t)
        + As * np.sin(omega[0] * t)
    )


def model3b(t, a, b, Ac, As):
    return (
        model1(t, a, b)
        + Ac * np.cos(omega[1] * t)
        + As * np.sin(omega[1] * t)        
    )


def model3(t, a, b, Ac1, As1, Ac2, As2):#, Ac3, As3):
    return (
        model1(t, a, b)
        + Ac1 * np.cos(omega[0] * t)
        + As1 * np.sin(omega[0] * t) 
        + Ac2 * np.cos(omega[1] * t)
        + As2 * np.sin(omega[1] * t)
    #    + Ac3 * np.cos(omega[2] * t)
    #    + As3 * np.sin(omega[2] * t)
               
    )


def model4(t, a, b, c, Ac1, As1, Ac2, As2):
    return (
        model2(t, a, b, c)
        + Ac1 * np.cos(omega[0] * t)
        + As1 * np.sin(omega[0] * t) 
        + Ac2 * np.cos(omega[1] * t)
        + As2 * np.sin(omega[1] * t)       
    )


def model5(t, a1, a2, b, delta_tsplit):
    #tsplit = 1985
    fac = (np.sign(t - delta_tsplit) + 1) / 2

    return (1 - fac) * (a1 * (t - delta_tsplit) + b) + fac * (a2 * (t - delta_tsplit) + b)


def model6(t, p0, p1, p2, p3, Ac0, As0, Ac1, As1, t0):
    """
    Everything is in
    """
    fac = (np.sign(t - t0) + 1) / 2

    linear = p0 + p1 * t
    jerky = fac * (((1/2) * p2 * (t - t0)**2) + ((1/6) * p3 * (t - t0)**3))
    oscillate = (
        Ac0 * np.cos(omega[0] * t) + As0 * np.sin(omega[0] * t) +
        Ac1 * np.cos(omega[1] * t) + As1 * np.sin(omega[1] * t)
    )
    return  linear + jerky + oscillate
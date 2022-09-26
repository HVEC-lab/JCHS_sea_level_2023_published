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


def model6(t, a, b, c):
    """
    Following KNMI TR318
    """
    return  (a * t) + (b * t**2) + (c * t**3)
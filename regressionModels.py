"""
Empirical sea level models
"""

import numpy as np

T = np.array([8.85 / 1, 18.61])  # Period of multi-year astronomical cycles
omega = (2 * np.pi) / T



def model1(t, a, b):
    """
    A simple linear trend. Used only during research
    """
    return b * t + a


def model2(t, a, b, c):
    """
    An accelerating signal. Used only during research
    """
    return c * t**2 + b * t + a


def model3a(t, a, b, Ac, As):
    """
    Linear model with only the 8.85 year tidal component.
    Not published; research only
    """
    return (
        model1(t, a, b)
        + Ac * np.cos(omega[0] * t)
        + As * np.sin(omega[0] * t)
    )


def model3b(t, a, b, Ac, As):
    """
    Linear model with only the nodal cycle included. Not published; research only
    """
    return (
        model1(t, a, b)
        + Ac * np.cos(omega[1] * t)
        + As * np.sin(omega[1] * t)        
    )


def harmonic(t, Ac1, As1, Ac2, As2):
    """
    Harmonic part of long term patterns
    """
    res = (
          Ac1 * np.cos(omega[0] * t)
        + As1 * np.sin(omega[0] * t) 
        + Ac2 * np.cos(omega[1] * t)
        + As2 * np.sin(omega[1] * t)
    )
    return res


def linear_fnc(t, a, b):
    """
    Linear part of the regression models
    """
    return a + b * t


def reducedModel(t, a, b, Ac1, As1, Ac2, As2):
    """
    The reduced model described in the paper, using a sine/cosine combination for
    the harmonic components instead of an amplitude/phase formulation.
    """
    return linear_fnc(t, a, b) + harmonic(t, Ac1, As1, Ac2, As2)


def jerked_fnc(t, p0, p1, p2, p3, t0):
    """
    Model with trend, acceleration and jerk starting at time t0
    """
    fac = (np.sign(t - t0) + 1) / 2

    linear = linear_fnc(t, p0, p1)
    jerky = fac * (((1/2) * p2 * (t - t0)**2) + ((1/6) * p3 * (t - t0)**3))
    return linear + jerky


def fullModel(t, p0, p1, p2, p3, Ac0, As0, Ac1, As1, t0):
    """
    The full model described in Voortman (2022), using a sine/cosine formula for the
    harmonic components instead of amplitude and phase angle.

    The model fully complies with contemporary insights in the effects of anthropogenic climate change
    on sea levels.
    """
    jerky = jerked_fnc(t, p0, p1, p2, p3, t0)
    oscillate = (
        Ac0 * np.cos(omega[0] * t) + As0 * np.sin(omega[0] * t)
        + Ac1 * np.cos(omega[1] * t) + As1 * np.sin(omega[1] * t)
    )
    return  jerky + oscillate

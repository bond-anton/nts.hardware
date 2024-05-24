"""Functions for film thickness calculation"""

import math as m


def freq_change_to_mass_per_cm2(f0, f1, z):
    """Calculate film mass per cm2"""
    nq = 1.668e5  # Hz*cm  Frequency const of AT-cut quatz
    rq = 2.648  # g/cm3 Density of quartz
    # mq = 2.947e11 # g/(cm*s2) Shear modulus of quartz
    return (
        nq * rq / (m.pi * z * f1) * m.atan(z * m.tan(m.pi * (f0 - f1) / f0))
    )  # g / cm2


def freq_change_to_thickness(f0, f1, r, z):
    """Calculate film thickness"""
    nq = 1.668e5  # Hz*cm  Frequency const of AT-cut quatz
    rq = 2.648  # g/cm3 Density of quartz
    # mq = 2.947e11 # g/(cm*s2) Shear modulus of quartz
    return (
        nq * rq / (m.pi * z * f1) * m.atan(z * m.tan(m.pi * (f0 - f1) / f0)) / r * 1e8
    )  # Angstrom

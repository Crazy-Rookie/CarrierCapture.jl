#!/usr/bin/env python3.7
# -*- coding=utf-8 -*-
"""
Get the mass weighted coordinate difference between two geometries.

The distance can be in a straight line, or projected on to a vector of initial and final geometries.

"""

import sys
import os
import argparse
import numpy as np

from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.io.vasp.inputs import Poscar, Kpoints
from pymatgen.core.structure import Structure

import matplotlib.pyplot as plt


def read_poscar(i_path, l_get_sorted_symbols=False):
    poscar = Poscar.from_file("{}".format(i_path))
    struct = poscar.structure
    if l_get_sorted_symbols:
        return struct, poscar.site_symbols
    else:
        return struct


def main(args):
    struct_i = read_poscar(args.init)
    struct_f, sorted_symbols = read_poscar(args.fin, True)
    delta_R = struct_f.frac_coords - struct_i.frac_coords
    delta_R = (delta_R + 0.5) % 1 - 0.5
    lattice = struct_i.lattice.matrix
    delta_R = np.dot(delta_R, lattice)

    masses = np.array([spc.atomic_mass for spc in struct_i.species])

    # allow for no mass weighting
    if args.no_weight:
        delta_Q2 = delta_R ** 2
    else:
        delta_Q2 = masses[:, None] * delta_R ** 2
    delta_Q = np.sqrt(delta_Q2.sum())

    print("Delta Q:", delta_Q)

    if args.med != "unassigned":
        struct_m = read_poscar(args.med)
        delta_M = struct_m.frac_coords - struct_i.frac_coords
        delta_M = (delta_M + 0.5) % 1 - 0.5
        delta_M = np.dot(delta_M, lattice)
        # project the midpoint on the delta_R vector
        # einsum for row-wise dot product
        dots = np.einsum("ij,ij->i", delta_R, delta_M)
        norm = np.linalg.norm(delta_R, axis=1)
        delta_M_proj = dots / norm

        frac_delta_M_proj = delta_M_proj/norm

        if args.no_weight:
            res = np.average(frac_delta_M_proj)
        else:
            res = np.average(frac_delta_M_proj, weights = np.sqrt(masses))

        print("Projected delta Q:", delta_Q*res)
        print("Fractional displacement:", res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="This script calculates the atomic mass weighted distance between two structures.",
    )
    parser.add_argument(
        "-i", "--init", help="initial input file (POSCAR format) ", default="./POSCAR_i"
    )
    parser.add_argument(
        "-f", "--fin", help="final input file (POSCAR format) ", default="./POSCAR_f"
    )
    parser.add_argument(
        "-m",
        "--med",
        nargs="?",
        default="unassigned",
        help="optional medium geometry (POSCAR format) to get its the fractional displacement between the initial and final geometries",
    )
    parser.add_argument(
        "-nw", "--no_weight", action="store_true", help="Turn off mass weighting"
    )

    args = parser.parse_args()

    main(args)

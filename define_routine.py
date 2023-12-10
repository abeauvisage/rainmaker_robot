import argparse
import curses
import json
import time

import numpy as np
import sympy as sp

from robotic_arm import RoboticArm
from servo import AngleError


L1 = 0.275
L2 = 0.375

parser = argparse.ArgumentParser(description="A simple program to test and configure the arm.")
parser.add_argument("-f", "--config-file", help="Path to an arm config file.", required=True)
parser.add_argument("-o", "--output-file", help="Path to a json file to save data.", required=True)


args = parser.parse_args()

arm = RoboticArm(args.config_file)
arm.reset()

checkpoints = []


def d(alpha1, alpha2):
    return (
        np.cos(alpha1) * L2 * np.cos(alpha2)
        - np.sin(alpha1) * L2 * np.sin(alpha2)
        - L1 * np.cos(alpha1)
    )


def h(alpha1, alpha2):
    return (
        np.sin(alpha1) * L2 * np.cos(alpha2)
        + np.cos(alpha1) * L2 * np.sin(alpha2)
        - L1 * np.sin(alpha1)
    )


def record_arrow_keys(stdscr):

    stdscr.clear()
    stdscr.addstr(0, 0, "Press arrow keys. Press 'q' to exit.")
    orientation = arm.get_angle("base")

    alpha1 = arm.get_angle("joint1")
    alpha2 = arm.get_angle("joint2")

    #  depth = (
    #      np.cos(alpha1) * L2 * np.cos(alpha2)
    #      - np.sin(alpha1) * L2 * np.sin(alpha2)
    #      + L1 * np.cos(alpha1)
    #  )

    #  height = (
    #      np.sin(alpha1) * L2 * np.cos(alpha2)
    #      + np.cos(alpha1) * L2 * np.sin(alpha2)
    #      + L1 * np.sin(alpha1)
    #  )

    #  stdscr.addstr(
    #      1,
    #      0,
    #      f"o: {orientation}, h: {h(alpha1, alpha2)}, d: {d(alpha1, alpha2)}, alpha1: "
    #      f"{arm.get_angle('joint2')}, alpha2: {alpha2}.",
    #  )

    #  alpha1, alpha2 = sp.symbols("alpha1 alpha2")
    #  depth_eq = (
    #      sp.cos(alpha1) * L2 * sp.cos(-alpha2)
    #      + sp.sin(alpha1) * L2 * sp.sin(-alpha2)
    #      + L1 * sp.cos(alpha1)
    #      - depth
    #  )

    dd_da1 = (
        -L1 * np.sin(alpha1)
        - L2 * np.cos(alpha2) * np.sin(alpha1)
        + L2 * np.sin(alpha2) * np.cos(alpha1)
    )
    #  dd_da1 = (
    #      -np.sin(alpha1) * L2 * np.cos(-alpha2)
    #      - np.cos(alpha1) * L2 * np.sin(-alpha2)
    #      - L1 * np.sin(alpha1)
    #  )
    dd_da2 = L2 * np.sin(alpha2 - alpha1)
    #  dd_da2 = (
    #      np.cos(alpha1) * L2 * np.sin(-alpha2)
    #      + np.sin(alpha1) * L2 * np.cos(-alpha2)
    #      + L1 * np.cos(alpha1)
    #  )

    dh_da1 = (
        L1 * np.cos(alpha1)
        + L2 * np.cos(alpha1) * np.cos(alpha2)
        + L2 * np.sin(alpha1) * np.sin(alpha2)
    )
    #  dh_da1 = (
    #  np.cos(alpha1) * L2 * np.cos(-alpha2)
    #  - np.sin(alpha1) * L2 * np.sin(-alpha2)
    #  + L1 * np.cos(alpha1)
    #  )
    dh_da2 = -L2 * np.cos(alpha1 - alpha2)
    #  dh_da2 = (
    #  np.sin(alpha1) * L2 * np.sin(-alpha2)
    #  - np.cos(alpha1) * L2 * np.cos(-alpha2)
    #  + L1 * np.sin(alpha1)
    #  )

    #  da1 = np.radians(10)
    #  da2 = np.radians(0)

    #  dd = dd_da1 * da1 + dd_da2 * da2
    #  dh = dh_da1 * da1 + dh_da2 * da2

    #  A = np.array([[dd_da1, dd_da2], [dh_da1, dh_da2]])
    #  y = np.array([0.01, 0.0])
    #  x = np.linalg.solve(A, y)

    #  dalpha1 = alpha1 + x[0]
    #  dalpha2 = alpha2 + x[1]

    #  stdscr.addstr(
    #      2,
    #      0,
    #      f"o: {orientation}, h: {h(alpha1+da1, alpha2+da2)}, d: {d(alpha1+da2, alpha2+da2)}, "
    #      f"o: {orientation}, h: {height+dh}, d: {depth+dd}, "
    #      f"alpha1: {alpha1+np.radians(1)}, "
    #      f"alpha2: {alpha2+np.radians(1)}, "
    #      f"alpha1: {A}, "
    #      f"alpha2: {x}.",
    #  )
    #  height_eq = (
    #      -sp.sin(alpha1) * L2 * sp.cos(-alpha2)
    #      + sp.cos(alpha1) * L2 * sp.sin(-alpha2)
    #      + L1 * sp.sin(alpha1)
    #      - height
    #  )

    #  solutions = sp.solve(depth_eq, alpha1, alpha2)
    #  stdscr.addstr(1, 0, f"{solutions}")

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            stdscr.addstr(1, 0, "Up      ")
            alpha1 += 1
            try:
                arm.move_servo("joint1", alpha1)
            except AngleError:
                continue
        if key == curses.KEY_RIGHT:
            stdscr.addstr(1, 0, "Right   ")
            try:
                arm.move_servo("base", orientation + 1)
            except AngleError:
                continue
            orientation += 1
        if key == curses.KEY_DOWN:
            stdscr.addstr(1, 0, "Down    ")
            alpha1 -= 1
            try:
                arm.move_servo("joint1", alpha1)
            except AngleError:
                continue
        if key == curses.KEY_LEFT:
            stdscr.addstr(1, 0, "Left    ")
            orientation -= 1
            try:
                arm.move_servo("base", orientation)
            except AngleError:
                continue
        if key == ord("a"):
            stdscr.addstr(1, 0, "A    ")
            alpha2 += 1
            try:
                arm.move_servo("joint2", alpha2)
            except AngleError:
                continue
        if key == ord("d"):
            stdscr.addstr(1, 0, "D    ")
            alpha2 -= 1
            try:
                arm.move_servo("joint2", alpha2)
            except AngleError:
                continue

        if key == ord("s"):
            checkpoints.append((orientation, alpha1, alpha2))
            stdscr.addstr(1, 0, "CP saved")

        if key == ord("q"):
            break

    curses.endwin()


curses.wrapper(record_arrow_keys)

arm.reset()

print("checkpoints", checkpoints)
with open(args.output_file, "w") as f:
    json.dump(checkpoints, f)

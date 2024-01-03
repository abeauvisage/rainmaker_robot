import argparse
import json
import time

import numpy as np

from robotic_arm import RoboticArm
from servo import AngleError


L1 = 0.275
L2 = 0.375

parser = argparse.ArgumentParser(description="A simple program to test and configure the arm.")
parser.add_argument("-f", "--config-file", help="Path to an arm config file.", required=True)
parser.add_argument("-r", "--routine-file", help="Path to a json routine_file.", required=True)
parser.add_argument("--dry-run", help="Run without using the pump.", action="store_true")

args = parser.parse_args()


def move_together(arm, name1, name2, angle1, angle2):
    start1 = arm.get_angle(name1)
    start2 = arm.get_angle(name2)
    n = max(np.abs(angle1 - start1), np.abs(angle2 - start2)) * 10

    s1 = np.linspace(start1, angle1, n)
    s2 = np.linspace(start2, angle2, n)

    for i in range(n):
        arm.move_servo(name1, s1[i])
        arm.move_servo(name2, s2[i])


with open(args.routine_file, "r") as f:
    routine = json.load(f)

    arm = RoboticArm(args.config_file)
    for pitstop in routine:
        if pitstop.get("checkpoint"):
            orientation, alpha1, alpha2 = pitstop["checkpoint"]
            arm.move_servo("base", orientation)
            move_together(arm, "joint1", "joint2", alpha1, alpha2)
            if args.dry_run:
                time.sleep(pitstop.get("duration", 0))
            else:
                arm.water(pitstop.get("duration", 0))
        move_together(
            arm,
            "joint1",
            "joint2",
            arm.get_default_angle("joint1"),
            arm.get_default_angle("joint2"),
        )
    arm.reset()

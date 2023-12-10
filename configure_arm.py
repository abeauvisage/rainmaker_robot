import argparse

from robotic_arm import RoboticArm

parser = argparse.ArgumentParser(description="A simple program to test and configure the arm.")
parser.add_argument("-f", "--config-file", help="Path to an arm config file.", required=True)


args = parser.parse_args()

arm = RoboticArm(args.config_file)

arm.reset()
print("The arm is now at default position.")
input("Press any key to continue...")
arm.default_routine()

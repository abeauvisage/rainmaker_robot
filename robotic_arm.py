import json

from adafruit_servokit import ServoKit

from servo import AngleError, ServoMotor

ARM_CONFIG_FIELDS = ("num_channels", "servos")
SERVO_CONFIG_FIELDS = ("name", "index", "min", "max", "default", "min_pulse", "max_pulse")


def load_config_file(filename: str):
    """Load and check that all data is available."""
    with open(filename) as f:
        config = json.load(f)

        for field in ARM_CONFIG_FIELDS:
            if not field in config.keys():
                print(f"Arm field {field} is missing from the config file.")
                return None

        for servo_config in config["servos"]:
            for field in SERVO_CONFIG_FIELDS:
                if not field in servo_config.keys():
                    print(f"Servo field {field} is missing from the config file.")
                    return None

        return config


class RoboticArm:
    """Class representing a robotic arm made of several servo motors"""

    def __init__(self, config_filename: str):

        config = load_config_file(config_filename)
        if not config:
            raise KeyError(f"Could not load the config file provided ({config_filename})")

        self._kit = ServoKit(channels=config["num_channels"])
        self._servos = {}
        self._servo_configs = {}
        for servo_config in config["servos"]:
            key = servo_config.pop("name")
            servo_config["servo"] = self._kit.servo[servo_config.pop("index")]
            self._servos[key] = ServoMotor(**servo_config)
            self._servo_configs[key] = servo_config

    def move_servo(self, name: str, angle: int):
        self._servos[name].to(angle)

    def get_angle(self, name: str) -> int:
        return self._servos[name].angle

    def get_default_angle(self, name: str) -> int:
        return self._servo_configs[name]["default"]

    def reset(self):
        for name, servo in self._servos.items():
            servo.reset()

    def default_routine(self):
        self.reset()
        for (name, servo), config in zip(self._servos.items(), self._servo_configs.values()):
            print(f"Rotating servo {name} to {config['max']}, then to {config['min']}")
            servo.to(config["max"])
            servo.to(config["min"])

        self.reset()

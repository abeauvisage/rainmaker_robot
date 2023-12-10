import time
from unittest.mock import MagicMock

from adafruit_motor.servo import Servo

UPDATE_RATE = 20  # Hz, degrees per second


class AngleError(Exception):
    def __init__(self, message="Wrong angle provided to the servo."):
        self.message = message
        super().__init__(self.message)


class ServoMotor:
    """Class representing a Servo motor"""

    def __init__(self, **kwargs):
        self.MIN = kwargs["min"]
        self.MAX = kwargs["max"]
        self.DEFAULT = kwargs["default"]
        self._angle = int(kwargs.get("angle", self.DEFAULT))
        if not kwargs["servo"]:
            raise TypeError("invalid Servo object provided!")
        self._motor = kwargs["servo"]
        self._motor.set_pulse_width_range(float(kwargs["min_pulse"]), float(kwargs["max_pulse"]))

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value: int):
        if self.MIN <= value <= self.MAX:
            self._angle = value
            self._motor.angle = value
            time.sleep(1.0 / UPDATE_RATE)
        else:
            raise AngleError(f"angle {value} not within the motor's range [{self.MIN},{self.MAX}]")

    def to(self, angle: int):
        if angle > self.angle:
            for i in range(self.angle, angle + 1, 1):
                self.angle = i
        else:
            if angle < self.angle:
                for i in range(self.angle, angle - 1, -1):
                    self.angle = i

    def reset(self):
        self.to(self.DEFAULT)


def test_value(name, current, expected):
    print(f"Test {name}: ", current == expected)
    if current != expected:
        print(f"Expected {expected} but got {current} instead!")


if __name__ == "__main__":

    servo_mock = MagicMock()
    servo_mock.set_pulse_width_range.return_value = None
    servo_mock.angle.return_value = None

    servo = ServoMotor(min=0, max=180, default=90, servo=servo_mock, min_pulse=50, max_pulse=100)

    try:
        servo.angle = -10
    except AngleError:
        pass
    test_value("too small", servo.angle, 90)

    try:
        servo.angle = 200
    except AngleError:
        pass
    test_value("too large", servo.angle, 90)

    servo.angle = 10
    test_value("correct angle", servo.angle, 10)

    servo.reset()
    test_value("reset", servo.angle, 90)

    try:
        servo = ServoMotor()
    except KeyError:
        print("Wrong initialization handled properly.")

    try:
        servo = ServoMotor(min=0, max=180, default=90, servo=None)
    except TypeError:
        print("Wrong initialization with servo handled properly.")

import unittest

from app.main import handle_command_action
from parser.parser import RESPParser


class TestCommandActions(unittest.TestCase):
    parser = RESPParser()

    def test_info_command(self):
        commands = [
            ["info", "replication"],
            ["INFO", "replication"],
            ["Info", "replication"],
            ["inFo", "replication"],
        ]

        for command in commands:
            response = handle_command_action(self.parser, command)
            response_string = response.decode("utf-8")

            self.assertTrue("role:master" in response_string)


if __name__ == '__main__':
    unittest.main()

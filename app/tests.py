import unittest

from app.config import Info
from app.main import handle_command_action


class TestCommandActions(unittest.TestCase):
    def test_info_command(self):
        commands = [
            ["info", "replication"],
            ["INFO", "replication"],
            ["Info", "replication"],
            ["inFo", "replication"],
        ]

        for command in commands:
            response = handle_command_action(command)
            response_string = response.decode("utf-8")

            self.assertTrue("role:master" in response_string)
            self.assertTrue(
                f"master_replid:{Info.get(Info.Keys.MASTER_REPL_ID)}" in response_string
            )
            self.assertTrue(
                f"master_repl_offset:{Info.get(Info.Keys.MASTER_REPL_OFFSET)}" in response_string
            )


if __name__ == '__main__':
    unittest.main()

import unittest

from app.commands import Command
from app.config import Config, Info
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

    def test_command_generation(self):
        commands = [
            Command.ping_command(),
            Command.echo_command("hello"),
            Command.set_command("key", "value"),
            Command.set_command("key", "value", "ex", "10"),
            Command.get_command("key"),
            Command.exists_command("key"),
            Command.info_command("replication"),
        ]
        expecteds = [
            [Command.PING],
            [Command.ECHO, "hello"],
            [Command.SET, "key", "value"],
            [Command.SET, "key", "value", "ex", "10"],
            [Command.GET, "key"],
            [Command.EXISTS, "key"],
            [Command.INFO, "replication"],
        ]

        for i in range(len(commands)):
            command = commands[i]
            expected = Config.get(Config.Keys.PARSER).encode(expecteds[i])

            self.assertEqual(command, expected)


if __name__ == '__main__':
    unittest.main()

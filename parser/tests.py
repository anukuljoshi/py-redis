import unittest

from parser.exceptions import ParserException
from parser.parser import RESPParser


class TestRESPParser(unittest.TestCase):

    def test_resp_parser_encode(self):
        parser = RESPParser()

        inputs = [
            # int
            10,
            -100,
            +50,
            # bool
            True,
            False,
            # simple string
            "foo",
            "bar",
            "12345",
            # bulk string
            "hello\r\nworld",
            "\r\n",
            # list
            ["ECHO", "hello"],
            ["SET", "mykey", "foo"],
            ["GET", "mykey"],
            ["SET", "key", 1],
            ["SET", "key", -10],
            ["SET", "key", True],
            ["SET", "key", [-10, "value", True]],
        ]
        expected_outputs = [
            # int
            b":10\r\n",
            b":-100\r\n",
            b":50\r\n",
            # bool
            b"#t\r\n",
            b"#f\r\n",
            # simple string
            b"+foo\r\n",
            b"+bar\r\n",
            b"+12345\r\n",
            # bulk string
            b"$12\r\nhello\r\nworld\r\n",
            b"$2\r\n\r\n\r\n",
            # array
            b"*2\r\n+ECHO\r\n+hello\r\n",
            b"*3\r\n+SET\r\n+mykey\r\n+foo\r\n",
            b"*2\r\n+GET\r\n+mykey\r\n",
            b"*3\r\n+SET\r\n+key\r\n:1\r\n",
            b"*3\r\n+SET\r\n+key\r\n:-10\r\n",
            b"*3\r\n+SET\r\n+key\r\n#t\r\n",
            b"*3\r\n+SET\r\n+key\r\n*3\r\n:-10\r\n+value\r\n#t\r\n",
        ]

        if len(inputs) != len(expected_outputs):
            print("length of inputs and expected_outputs do not match")
            return

        for i in range(len(inputs)):
            output = parser.encode(inputs[i])
            self.assertEqual(
                output,
                expected_outputs[i],
                f"Failed {i}: output={output}, expected={expected_outputs[i]}"
            )

    def test_resp_parser_decode(self):
        parser = RESPParser()
        inputs = [
            # int
            b":5\r\n",
            b":123\r\n",
            b":1a5\r\n",
            # bool
            b"#t\r\n",
            b"#f\r\n",
            b"#j\r\n",
            # simple strings
            b"+abcd\r\n",
            b"+hello\r\n",
            # bulk strings
            b"$4\r\nabcd\r\n",
            b"$11\r\nhello world\r\n",
            b"$11\r\nhello\r\ntest\r\n",
            # list
            b"*3\r\n:12\r\n#t\r\n+hello\r\n",
            b"*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n*3\r\n:-10\r\n$5\r\nvalue\r\n#t\r\n",
            b"*3\r\n*2\r\n*1\r\n:1\r\n*3\r\n#t\r\n:25\r\n+hello 123 world\r\n*1\r\n$7\r\nhello\r\n\r\n*3\r\n:-40\r\n+50\r\n:+60\r\n",
            b"*1\r\n*2\r\n*1\r\n*1\r\n:1\r\n:12\r\n",
            # exception
            b"*1\r\n:2\r\n3",
        ]
        expected_outputs = [
            5,
            123,
            "ParserException",
            True,
            False,
            "ParserException",
            "abcd",
            "hello",
            "abcd",
            "hello world",
            "hello\r\ntest",
            [12, True, "hello"],
            ["SET", "key", [-10, "value", True]],
            [
                [[1], [True, 25, "hello 123 world"]],
                ["hello\r\n"],
                [-40, "50", 60],
            ],
            [
                [
                    [[1]],  12
                ]
            ],
            "ParserException",
        ]

        if len(inputs) != len(expected_outputs):
            print("length of inputs and expected_outputs do not match")
            return

        for i in range(len(inputs)):
            if expected_outputs[i] == "ParserException":
                self.assertRaises(ParserException, parser.decode, inputs[i])
            else:
                output = parser.decode(inputs[i])
                self.assertEqual(
                    output,
                    expected_outputs[i],
                    f"Failed {i}: output={output}, expected={expected_outputs[i]}"
                )

    def test_resp_parser_decode_command_string(self):
        parser = RESPParser()
        inputs = [
            # list
            b"*3\r\n:12\r\n#t\r\n+hello\r\n",
            b"*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n*3\r\n:-10\r\n$5\r\nvalue\r\n#t\r\n",
            b"*3\r\n*2\r\n*1\r\n:1\r\n*3\r\n#t\r\n:25\r\n+hello 123 world\r\n*1\r\n$7\r\nhello\r\n\r\n*3\r\n:-40\r\n+50\r\n:+60\r\n",
            b"*1\r\n*2\r\n*1\r\n*1\r\n:1\r\n:12\r\n",
            # exception
            b"*1\r\n:2\r\n3",
        ]
        expected_outputs = [
            [12, True, "hello"],
            ["SET", "key", [-10, "value", True]],
            [
                [[1], [True, 25, "hello 123 world"]],
                ["hello\r\n"],
                [-40, "50", 60],
            ],
            [
                [
                    [[1]],  12
                ]
            ],
            "ParserException",
        ]

        if len(inputs) != len(expected_outputs):
            print("length of inputs and expected_outputs do not match")
            return

        for i in range(len(inputs)):
            if expected_outputs[i] == "ParserException":
                self.assertRaises(ParserException, parser.decode, inputs[i])
            else:
                output = parser.decode_command(inputs[i])
                self.assertEqual(
                    output,
                    expected_outputs[i],
                    f"Failed {i}: output={output}, expected={expected_outputs[i]}"
                )


if __name__ == '__main__':
    unittest.main()

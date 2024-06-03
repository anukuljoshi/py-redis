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
            ":10\r\n",
            ":-100\r\n",
            ":50\r\n",
            # bool
            "#t\r\n",
            "#f\r\n",
            # simple string
            "+foo\r\n",
            "+bar\r\n",
            "+12345\r\n",
            # bulk string
            "$12\r\nhello\r\nworld\r\n",
            "$2\r\n\r\n\r\n",
            # array
            "*2\r\n+ECHO\r\n+hello\r\n",
            "*3\r\n+SET\r\n+mykey\r\n+foo\r\n",
            "*2\r\n+GET\r\n+mykey\r\n",
            "*3\r\n+SET\r\n+key\r\n:1\r\n",
            "*3\r\n+SET\r\n+key\r\n:-10\r\n",
            "*3\r\n+SET\r\n+key\r\n#t\r\n",
            "*3\r\n+SET\r\n+key\r\n*3\r\n:-10\r\n+value\r\n#t\r\n",
        ]

        if len(inputs) != len(expected_outputs):
            print("length of inputs and expected_outputs do not match")
            return

        for i in range(len(inputs)):
            output = parser.encode(inputs[i])
            self.assertEqual(
                output,
                expected_outputs[i],
                f"Failed {i}: output={output.encode('utf-8')}, expected={expected_outputs[i].encode('utf-8')}"
            )

    def test_resp_parser_decode(self):
        parser = RESPParser()
        inputs = [
            # int
            ":5\r\n",
            ":123\r\n",
            ":1a5\r\n",
            # bool
            "#t\r\n",
            "#f\r\n",
            "#j\r\n",
            # simple strings
            "+abcd\r\n",
            "+hello\r\n",
            # bulk strings
            "$4\r\nabcd\r\n",
            "$11\r\nhello world\r\n",
            "$11\r\nhello\r\ntest\r\n",
            # list
            "*3\r\n:12\r\n#t\r\n+hello\r\n",
            "*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n*3\r\n:-10\r\n$5\r\nvalue\r\n#t\r\n",
            "*3\r\n*2\r\n*1\r\n:1\r\n*3\r\n#t\r\n:25\r\n+hello 123 world\r\n*1\r\n$7\r\nhello\r\n\r\n*3\r\n:-40\r\n+50\r\n:+60\r\n",
            "*1\r\n*2\r\n*1\r\n*1\r\n:1\r\n:12\r\n",
            # exception
            "*1\r\n:2\r\n3",
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


if __name__ == '__main__':
    unittest.main()

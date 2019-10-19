import sys
from typing import List, Optional


class Architecture:
    debug = False

    math_op = 32768

    registers = {
        32768: 0,
        32769: 0,
        32770: 0,
        32771: 0,
        32772: 0,
        32773: 0,
        32774: 0,
        32775: 0,
    }

    character_input = list()

    stack: List[Optional[hex]] = list()

    def __init__(self, file: str, route: List[str]):
        self.character_input = list(route)
        self.stream = self.get_data_stream(file)
        self.process_stream()

    def debug_op_code_result(self, *args):
        names = {
            0: "halt",
            1: "set",
            2: "push",
            3: "pop",
            4: "eq",
            5: "gt",
            6: "jmp",
            7: "jt",
            8: "jf",
            9: "add",
            10: "multi",
            11: "mod",
            12: "and",
            13: "or",
            14: "not",
            15: "rmem",
            16: "wmem",
            17: "call",
            18: "ret",
            19: "out",
            20: "in",
            21: "noop",
        }
        index, op_code, *items = args
        if self.debug is True:
            print(op_code, f"<{names[op_code]}>", items, f"-> {self.stream[index + 1]}")
            print(f"\tR: {self.registers}")
            print(f"\tS: {self.stack}")

    def get_next_byte(self, index, register_check=False):
        index += 1
        arg1 = self.stream[index]
        if register_check:
            arg1 = self.register_check(arg1)
        return index, arg1

    def process_stream(self):
        index = 0

        while True:
            index, op_code = self.get_next_byte(index, register_check=True)

            if op_code == 0:
                sys.exit()

            elif op_code == 1:
                # set arg1 register to arg2
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                self.registers[arg1] = arg2
                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 2:
                # push(a) to stack
                index, arg1 = self.get_next_byte(index, register_check=True)
                self.stack.append(arg1)
                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 3:
                # pop off stack and write to register (a)
                index, arg1 = self.get_next_byte(index)
                self.registers[arg1] = self.stack.pop()
                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 4:
                # equal - set a to 1 if b == c else 0
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)
                self.registers[arg1] = 1 if arg2 == arg3 else 0
                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 5:
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)
                self.registers[arg1] = 1 if arg2 > arg3 else 0
                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 6:  # jump(a)
                index, arg1 = self.get_next_byte(index, register_check=True)
                index = arg1 - 1
                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 7:
                """JT: if a is nonzero jump to b"""
                index, arg1 = self.get_next_byte(index, register_check=True)
                index, arg2 = self.get_next_byte(index, register_check=True)

                if arg1 != 0:
                    index = arg2 - 1

                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 8:
                """JF: if a is zero jump to b"""
                index, arg1 = self.get_next_byte(index, register_check=True)
                index, arg2 = self.get_next_byte(index, register_check=True)
                if arg1 == 0:
                    index = arg2 - 1

                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 9:
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = (arg2 + arg3) % self.math_op
                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 10:  # mult
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = (arg2 * arg3) % self.math_op
                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 11:  # mod
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)
                self.registers[arg1] = (arg2 % arg3) % self.math_op

            elif op_code == 12:
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = arg2 & arg3  # % self.math_op

                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 13:
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)
                index, arg3 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = arg2 | arg3  # % self.math_op

                self.debug_op_code_result(index, op_code, arg1, arg2, arg3)

            elif op_code == 14:
                """bitwise inverse of <b> in <a>"""
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)

                inverse = (1 << 15) - 1 - arg2
                inverse_arg2 = self.register_check(inverse)
                self.registers[arg1] = inverse_arg2

                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 15:
                """rmem: read memory at address <b> and write it to <a>"""
                index, arg1 = self.get_next_byte(index, register_check=False)
                index, arg2 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = self.stream[arg2]
                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 16:
                """wmem: write the value from <b> into memory at address <a>"""
                index, arg1 = self.get_next_byte(index, register_check=True)
                index, arg2 = self.get_next_byte(index, register_check=True)

                self.stream[arg1] = arg2
                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 17:
                """Write next address to stack and jump to address"""
                index, arg1 = self.get_next_byte(index, register_check=True)
                self.stack.append(index + 1)
                index = arg1 - 1

                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 18:
                if len(self.stack) == 0:
                    sys.exit(1)

                item = self.stack.pop()
                index = item - 1
                self.debug_op_code_result(index, op_code, item)

            elif op_code == 19:
                """Print Next Character."""
                index, arg1 = self.get_next_byte(index, register_check=True)

                print(chr(arg1), end="")

                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 20:

                """read a character from the terminal and write its ascii code to <a>; 
                it can be assumed that once input starts, it will continue until a newline
                is encountered; this means that you can safely read whole lines from the
                keyboard and trust that they will be fully read"""
                if len(self.character_input) == 0:
                    self.character_input = list(input())
                    self.character_input.append("\n")

                if "".join(self.character_input[0:14]) == "use teleporter":
                    self.registers[32775] = 5605
                    # self.registers[32775] = 1000
                    print(self.stream[index:])
                result = self.character_input.pop(0)

                index, arg1 = self.get_next_byte(index, register_check=False)
                self.registers[arg1] = ord(result[0])

                # Printing out the next set of bytes revealed that the next logical op_code
                # instruction wants to match the input to a different register.  By simply typing
                # \n I was able to unlock additional messages/commands/etc.
                self.debug_op_code_result(index, op_code, result)

            elif op_code == 21:
                self.debug_op_code_result(index, op_code)
                pass
            else:
                # Should NEVER get here...
                raise ValueError(f"Unexpected op_code encountered: {op_code}")

    def register_check(self, arg):
        if 32768 <= arg <= 32775:
            # print(f"Updating {arg} to {self.registers[arg]}")
            arg = self.registers[arg]
        return arg

    @staticmethod
    def get_data_stream(file) -> List[int]:
        collector: List[int] = list()

        with open(file, "rb") as f:
            data = f.read(2)
            while data:
                byte = int.from_bytes(data, byteorder="little")
                collector.append(byte)
                data = f.read(2)

        return collector


def create_route():
    with open(r"./data/route.txt", "rt") as text:
        return text.read()


if __name__ == "__main__":
    route = create_route()
    f = r"data/synacor-challenge/challenge.bin"
    a = Architecture(f, route)

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

    stack: List[Optional[hex]] = list()

    def __init__(self, file: str):
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

            elif op_code == 15:  # rmem
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)

                self.registers[arg1] = self.stream[arg2]
                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 16:  # wmem
                index, arg1 = self.get_next_byte(index)
                index, arg2 = self.get_next_byte(index, register_check=True)

                self.stream[self.registers[arg1]] = arg2

                self.debug_op_code_result(index, op_code, arg1, arg2)

            elif op_code == 17:
                """Write next address to stack and jump to address"""
                index, arg1 = self.get_next_byte(index, register_check=True)
                self.stack.append(index+1)
                index = arg1 - 1

                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 18:
                if len(self.stack) == 0:
                    sys.exit()

                item = self.stack.pop()
                index = item - 1
                self.debug_op_code_result(index, op_code, item)
            elif op_code == 19:
                """Print Next Character."""
                index, arg1 = self.get_next_byte(index)

                print(chr(arg1), end='')

                self.debug_op_code_result(index, op_code, arg1)

            elif op_code == 20:
                raise NotImplemented

            elif op_code == 21:
                self.debug_op_code_result(index, op_code)
                pass
            else:
                # Should NEVER get here...
                print(op_code)
                raise ValueError

    def register_check(self, arg):
        if 32768 <= arg <= 32775:
            # print(f"Updating {arg} to {self.registers[arg]}")
            arg = self.registers[arg]
        return arg

    @staticmethod
    def get_data_stream(file) -> List[int]:
        collector: List[int] = list()

        with open(file, 'rb') as f:
            data = f.read(2)
            while data:
                byte = int.from_bytes(data, byteorder='little')
                collector.append(byte)
                data = f.read(2)

        return collector


if __name__ == "__main__":
    f = r"data/synacor-challenge/challenge.bin"
    a = Architecture(f)


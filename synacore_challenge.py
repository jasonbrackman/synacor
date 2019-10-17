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

    def process_stream(self):
        index = 0
        stream = self.stream
        while True:
            current = self.register_check(stream[index])
            if current == 0:
                sys.exit()

            elif current == 1:
                # set(a, b)
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                self.registers[arg1] = arg2

                if self.debug:
                    print("1", arg1, arg2, f"-> {stream[index+1]}")

            elif current == 2:
                # push(a) to stack
                index += 1
                arg1 = self.register_check(stream[index])

                self.stack.append(arg1)
                if self.debug:
                    print("2", arg1, f"-> {stream[index+1]}")

            elif current == 3:
                # pop off stack and write to register (a)
                index += 1
                arg1 = stream[index]
                self.registers[arg1] = self.stack.pop()
                if self.debug:
                    print(3, f"-> {stream[index+1]}")

            elif current == 4:
                # equal - set a to 1 if b == c else 0
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])

                self.registers[arg1] = 1 if arg2 == arg3 else 0

                if self.debug:
                    print("4", arg2, arg3, f"-> {stream[index + 1]}")

            elif current == 5:
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])

                self.registers[arg1] = 1 if arg2 > arg3 else 0
                if self.debug:
                    print("5", arg2, arg3, f"-> {stream[index+1]}")

            elif current == 6:  # jump(a)
                index += 1
                index = self.register_check(stream[index]) - 1
                if self.debug:
                    print(6, f"Jump({index}) -> {stream[index+1]}")

            elif current == 7:
                """JT: if a is nonzero jump to b"""
                index += 1
                arg1 = self.register_check(stream[index])

                index += 1
                arg2 = self.register_check(stream[index])

                if arg1 != 0:
                    index = arg2 - 1

                if self.debug:
                    print(7, arg1, arg2, f"-> {stream[index+1]}")

            elif current == 8:
                """JF: if a is zero jump to b"""
                index += 1
                arg1 = self.register_check(stream[index])

                index += 1
                arg2 = self.register_check(stream[index])

                if arg1 == 0:
                    index = arg2 - 1

                if self.debug:
                    print(8, arg1, arg2, f"-> {stream[index+1]}")

            elif current == 9:
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])

                self.registers[arg1] = (arg2 + arg3) % self.math_op
                if self.debug:
                    print("9", arg1, arg2, arg3, f"-> {stream[index+1]}")

            elif current == 10:
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])

                self.registers[arg1] = (arg2 * arg3) % self.math_op
                if self.debug:
                    print("10", arg1, arg2, arg3, f"-> {stream[index + 1]}")

            elif current == 11:
                raise ValueError

            elif current == 12:
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])

                self.registers[arg1] = arg2 & arg3  # % self.math_op
                if self.debug:
                    print("12", arg2, arg3, f"{stream[index+1]}")

            elif current == 13:
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                index += 1
                arg3 = self.register_check(stream[index])
                self.registers[arg1] = arg2 | arg3  # % self.math_op
                if self.debug:
                    print(13, arg2, arg3, f"{stream[index+1]}")

            elif stream[index] == 14:
                """bitwise inverse of <b> in <a>"""
                index += 1
                arg1 = stream[index]

                index += 1
                arg2 = self.register_check(stream[index])

                inverse = (1 << 15) - 1 - arg2
                inverse_arg2 = self.register_check(inverse)
                self.registers[arg1] = inverse_arg2

                if self.debug:
                    print(14, arg1, inverse_arg2, f"-> {stream[index+1]}")

            elif stream[index] == 15:
                raise ValueError

            elif stream[index] == 16:
                raise ValueError

            elif current == 17:
                """Write address to stack and jump to address"""
                index += 1
                self.stack.append(index)
                index = self.register_check(stream[index]) - 1

                if self.debug:
                    print(17, index, f"-> {stream[index+1]}")

            elif current == 18:
                raise ValueError

            elif current == 19:
                """Print Next Character."""
                index += 1
                arg1 = self.register_check(stream[index])

                print(chr(arg1), end='')

                if self.debug:
                    print(19, arg1, f"-> {stream[index+1]}")

            elif current == 20:
                raise NotImplemented

            elif current == 21:
                pass
            else:
                # Should NEVER get here...
                raise ValueError

            index += 1

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


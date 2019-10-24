import sys
import copy

from typing import List, Optional


class Machine:
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
    pointer: int = 0

    # hack the machine
    override_check: str = ""
    restore_point = None

    def __init__(self, file: str, route: List[str], override: int = 0):
        self.character_input = list(route)
        self.stream = self.get_data_stream(file)
        self.override = override

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
        description = {
            1458: "Commands to get appropriate character to print starts here...",
            1484: "Interesting counter -- if the two args equal some logic can happen, like 'is room yellow or red, etc'",
            1528: "print_buffer...",
            1531: "push onto the stack, set a register value, and call a function ... ",
            2125: "Feels like a math operation in this block? Two items pushed to stack, and/not/or and then stores info to registers.",
            1807: "Storing input character value ... ",
            2144: "Register updated to new value... Note that register 32768 is also manipulated above.",
            2146: "Reset register to what it was before the call started...",


        }

        index, op_code, *items = args
        if self.debug is True:
            actuals = [self.register_check(i) for i in items]

            results = list()
            for t in zip(items, actuals):
                if t[0] == t[1]:
                    results.append(f"[{t[0]}]")
                else:
                    results.append("[{}: {}]".format(t[0], t[1]))
            if op_code == 19:
                print()

            print(
                f"{index - len(results):05d}",
                f"{op_code:02d}",
                f"{names[op_code]:>6}",
                *results,
                f"-> {self.stream[index + 1]}",
                f"\t\t\t{description.get(index - len(results), '')}",
            )



    def get_next_byte(self, index, register_check=False):
        index += 1
        arg1 = self.stream[index]
        if register_check:
            arg1 = self.register_check(arg1)
        return index, arg1

    def process_stream(self):
        while True:
            self.pointer, op_code = self.get_next_byte(
                self.pointer, register_check=True
            )

            if op_code == 0:
                """halt 0 -> stop execution and terminate the program"""
                sys.exit()

            elif op_code == 1:
                """set: 1 a b -> set register <a> to the value of <b>"""
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.registers[arg1] = arg2
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 2:
                """push: 2 a -> push <a> onto the stack"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.stack.append(arg1)
                self.debug_op_code_result(self.pointer, op_code, arg1)

            elif op_code == 3:
                # pop off stack and write to register (a)
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.registers[arg1] = self.stack.pop()
                self.debug_op_code_result(self.pointer, op_code, arg1)

            elif op_code == 4:
                # equal - set a to 1 if b == c else 0
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.registers[arg1] = 1 if arg2 == arg3 else 0
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 5:
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.registers[arg1] = 1 if arg2 > arg3 else 0
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 6:  # jump(a)
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer = arg1 - 1
                self.debug_op_code_result(self.pointer, op_code, arg1)

            elif op_code == 7:
                """JT: if a is nonzero jump to b"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                # HACK for verification code to be short circuited
                if self.registers[32775] != 0 and arg2 == 6048:
                    # print(arg1, arg2)
                    arg1 = 0
                    # self.debug = False
                if arg1 != 0:
                    self.pointer = arg2 - 1

                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 8:
                """JF: if a is zero jump to b"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                if arg1 == 0:
                    self.pointer = arg2 - 1

                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 9:
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.registers[arg1] = (arg2 + arg3) % self.math_op
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 10:  # mult
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.registers[arg1] = (arg2 * arg3) % self.math_op
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 11:  # mod
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.registers[arg1] = (arg2 % arg3) % self.math_op

            elif op_code == 12:
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.registers[arg1] = arg2 & arg3

                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 13:
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg3 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.registers[arg1] = arg2 | arg3

                self.debug_op_code_result(self.pointer, op_code, arg1, arg2, arg3)

            elif op_code == 14:
                """bitwise inverse of <b> in <a>"""
                self.pointer, arg1 = self.get_next_byte(self.pointer)
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                inverse = (1 << 15) - 1 - arg2
                inverse_arg2 = self.register_check(inverse)
                self.registers[arg1] = inverse_arg2

                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 15:
                """rmem: read memory at address <b> and write it to <a>"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=False
                )
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.registers[arg1] = self.stream[arg2]
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 16:
                """wmem: write the value from <b> into memory at address <a>"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.pointer, arg2 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                self.stream[arg1] = arg2
                self.debug_op_code_result(self.pointer, op_code, arg1, arg2)

            elif op_code == 17:
                """Write next address to stack and jump to address"""
                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )
                self.stack.append(self.pointer + 1)
                self.pointer = arg1 - 1

                self.debug_op_code_result(self.pointer, op_code, arg1)

            elif op_code == 18:
                if len(self.stack) == 0:
                    sys.exit(1)

                item = self.stack.pop()
                self.pointer = item - 1
                self.debug_op_code_result(self.pointer, op_code, item)

            elif op_code == 19:
                """Print Next Character."""

                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=True
                )

                print(chr(arg1), end="")

                # Hack the machine for teleportation
                self.hack_the_machine(arg1)

                self.debug_op_code_result(self.pointer, op_code, arg1)

            elif op_code == 20:

                """read a character from the terminal and write its ascii code to <a>; 
                it can be assumed that once input starts, it will continue until a newline
                is encountered; this means that you can safely read whole lines from the
                keyboard and trust that they will be fully read"""
                if len(self.character_input) == 0:
                    self.character_input = list(input())
                    self.character_input.append("\n")

                self.hack_orb()

                # IMPORTANT: Change the 8th register at this point to pass initial
                # machine startup tests -- but to then be ready for teleportation.
                if "".join(self.character_input).startswith("use teleporter\n"):
                    self.registers[32775] = self.override

                result = ord(self.character_input.pop(0))

                self.pointer, arg1 = self.get_next_byte(
                    self.pointer, register_check=False
                )

                self.registers[arg1] = result

                # Printing out the next set of bytes revealed that the next logical op_code
                # instruction wants to match the input to a different register.  By simply typing
                # \n I was able to unlock additional messages/commands/etc.
                self.debug_op_code_result(self.pointer, op_code, result)

            elif op_code == 21:
                self.debug_op_code_result(self.pointer, op_code)
                pass
            else:
                # Should NEVER get here...
                raise ValueError(f"Unexpected op_code encountered: {op_code}")

    def hack_orb(self):
        if "".join(self.character_input).startswith("use orb\n"):
            self.debug = not self.debug

    def hack_the_machine(self, arg1):
        if (
            "".join(self.character_input).startswith("use teleporter\n")
            and self.registers[32775] == 0
        ):
            if self.restore_point is None:
                # Create a point to get back to in order to loop faster.
                # and hack the Machine for its stabilization number.
                self.restore_point = copy.deepcopy(self)

            # Only takes place when 'use teleporter' is triggered
            self.registers[32775] = self.override

        if self.registers[32775] != 0:
            self.override_check += chr(arg1)

            # Message seen if we don't hack the machine and SLOW verification takes place
            if "1 billion years" in self.override_check:
                pass
                # This was used to trace the machine code that caused the verification
                # While teh code is no longer needed with the solution -- keeping it
                # for posterity :)
                # self.debug = True

            # When brute forcing the code, many attempts will be made, and this message
            # indicates verification took place, but failed
            if "Nothing else seems to happen." in self.override_check:

                # failed to resolve teleporter code -- so lets restore the machine state
                # and try again
                print(
                    f"\nRestoring the world...: Register 32775: {self.registers[32775]}"
                )
                self.registers = dict(self.restore_point.registers)
                self.stack = list(self.restore_point.stack)
                self.stream = list(self.restore_point.stream)
                self.override_check = self.restore_point.override_check[::]
                self.character_input = list(self.restore_point.character_input)
                self.pointer = self.restore_point.pointer
                self.override += 1
                self.registers[32775] = self.override

    def register_check(self, arg):
        if isinstance(arg, int) is False:
            raise TypeError(
                f"expected an int, but instead received {type(arg)} -> {arg}"
            )
        if 32768 <= arg <= 32775:
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


def main(f, route, i):
    a = Machine(f, route, i)
    a.process_stream()


if __name__ == "__main__":
    route = create_route()
    f = r"data/synacor-challenge/challenge.bin"
    teleportation_calibration_code = 32773
    main(f, route, teleportation_calibration_code)

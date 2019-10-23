"""
                             Door = 30
                             Pedestal = 22
                  * 8 -  1   y
                  4 * 11 *   g y y y
                  + 4 - 18   g y r y
                 22 - 9 *    n r r y
"""

from typing import Tuple

from collections import namedtuple

Direction = namedtuple("Direction", ['north', 'south', 'east', 'west'])

class Cave:

    board = [
        ['*', 8, '-', 1],
        [4, '*', 11, '*'],
        ['+', 4, '-', 18],
        [22, '-', 9, '*'],
    ]

    DIRECTION = Direction(
        north=(-1, 0),
        south=(1, 0),
        east=(0, 1),
        west=(0, -1)
    )

    GOAL = 30

    def __init__(self, start: Tuple = (3, 0)):
        self.position = start
        self.total = 0

    def add_positions(self, pos01, pos02):
        x = pos01[0] + pos02[0]
        y = pos01[1] + pos02[1]
        return x, y

    def is_legal(self, x, y) -> bool:
        return 0 <= x < len(self.board) and 0 <= y < len(self.board)


    def successors(self):
        collector = list()
        for dir in self.DIRECTION:
            x, y = self.add_positions(self.position, dir)
            if self.is_legal(x, y) is True:
                collector = (x, y)
        return collector

    def goal(self):
        return self.total == self.GOAL and self.position == (0, 3)


if __name__ == "__main__":
    cave = Cave()
    cave.successors()
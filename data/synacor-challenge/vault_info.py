"""
                             Door = 30
                             Pedestal = 22
                  * 8 -  1   y
                  4 * 11 *   g y y y
                  + 4 - 18   g y r y
                 22 - 9 *    n r r y
"""

from collections import namedtuple

Direction = namedtuple("Direction", ['north', 'south', 'east', 'west'])

class Cave:

    board = [
        ['*', 8, '-', 1],
        [4, '*', 11, '*'],
        ['+', 4, '-', 18],
        [22, '-', 9, '*'],
    ]

    direction = Direction(
        north=(-1, 0),
        south=(1, 0),
        east=(0, 1),
        west=(0, -1)
    )

    GOAL = 30

    def __init__(self, start: (3, 0)):
        self.position = start
        self.total = 0

    def successors(self, position):
        ...

    def goal(self):
        return self.total == self.GOAL and self.position == (0, 3)




print((22 + 4 - 18) * 1)
print(22-9-11-1)
print((22 - 4) * 4 * 8 - 1)
print()

print((22-9) * 18 * 11 * 4)

print("J", 22+4*8)

x = [22-9, 22+4, 22+4]
y = []
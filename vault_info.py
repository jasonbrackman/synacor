"""
                             Door = 30
                             Pedestal = 22
                  * 8 -  1   y
                  4 * 11 *   g y y y
                  + 4 - 18   g y r y
                 22 - 9 *    n r r y
"""
from __future__ import annotations

from typing import (
    Deque,
    Tuple,
    Callable,
    List,
    Optional,
    Generic,
    TypeVar,
    Set,
    NamedTuple,
)
from collections import deque
from collections import namedtuple

T = TypeVar("T")

Direction = namedtuple("Direction", ["north", "south", "east", "west"])


class LocValue(NamedTuple):
    pos: Tuple
    value: int
    operator: str
    direction: str
    last_pos: Optional[Tuple]


class Cave:

    board = [["*", 8, "-", 1], [4, "*", 11, "*"], ["+", 4, "-", 18], [22, "-", 9, "*"]]

    DIRECTION = Direction(north=(-1, 0), south=(1, 0), east=(0, 1), west=(0, -1))
    MAPPINGS = {
        DIRECTION.north: "north",
        DIRECTION.south: "south",
        DIRECTION.east: "east",
        DIRECTION.west: "west",
    }
    GOAL = 30

    def __init__(self, start: LocValue):
        self.state = start

    def add_positions(self, pos01, pos02):
        x = pos01[0] + pos02[0]
        y = pos01[1] + pos02[1]
        return x, y

    def is_legal(self, x, y) -> bool:
        if (x, y) == self.state.last_pos and isinstance(self.state.operator, str):
            return False

        if x < 0 or y < 0:
            return False

        if x >= len(self.board) or y >= len(self.board):
            return False

        return True

    def successors(self) -> List[Cave]:
        min_number = -40
        max_number = 100
        collector = list()
        for direction in self.DIRECTION:

            x, y = self.add_positions(self.state.pos, direction)
            if self.is_legal(x, y) is True:
                where_am_i = self.MAPPINGS[direction]
                room_value = self.board[x][y]
                total_weight = self.state.value

                if isinstance(room_value, int):
                    if self.state.operator == "-":
                        total_weight -= room_value
                    if self.state.operator == "+":
                        total_weight += room_value
                    if self.state.operator == "*":
                        total_weight *= room_value

                if (x, y) == (3, 0):
                    total_weight = 22

                if max_number >= total_weight > min_number:
                    collector.append(
                        Cave(
                            LocValue(
                                pos=(x, y),
                                value=total_weight,
                                operator=room_value,
                                direction=where_am_i,
                                last_pos=self.state.pos,
                            )
                        )
                    )

        return collector

    def goal_test(self):
        return self.state.value == self.GOAL and self.state.pos == (0, 3)


class Node(Generic[T]):
    def __init__(
        self,
        state: T,
        parent: Optional[Node],
        cost: float = 0.0,
        heuristic: float = 0.0,
    ) -> None:
        """

        :param state: The Node identity to be compared to another Node.
        :param parent:
        :param cost:
        :param heuristic:
        """
        self.state: T = state
        self.parent: Optional[Node] = parent
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


class Queue(Generic[T]):
    """
    FIFO Structure:
    - always append to the right
    - always pop from the left
    """

    def __init__(self) -> None:
        # While the book uses Deque -- it isn't recognized by PyCharm.  The idea is
        # that the Deque is an 'analog' for the collections.deque()... probably helps
        # when defining internal types of the container.
        self._container: Deque[T] = deque()

    @property
    def empty(self) -> bool:
        return not self._container  # not is true for empty container

    def push(self, item: T) -> None:
        self._container.append(item)

    def pop(self) -> T:
        return self._container.popleft()  # FIFO

    def __repr__(self) -> str:
        return repr(self._container)


def bfs(
    initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]]
) -> Optional[Node[T]]:
    # frontier is where we've yet to go
    frontier: Queue[Node[T]] = Queue()
    frontier.push(Node(initial, None))  # explored is where we've been

    explored: Set[T] = {initial}

    # keep going while there is more to explore
    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state  # if we found the goal, we're done
        if goal_test(current_state):
            return current_node

        # check where we can go next and haven't explored
        for child in successors(current_state):
            if child in explored:  # skip children we already explored
                continue
            explored.add(child)
            frontier.push(Node(child, current_node))

    return None


def node_to_path(node: Node[T]) -> List[T]:
    path: List[T] = [node.state]
    # work backwards from end to front
    while node.parent is not None:
        node = node.parent
        if node.state.state.pos == (3, 0):
            # path.append("take orb")
            ...
        path.append(node.state)

    path.reverse()

    return path


if __name__ == "__main__":
    cave = Cave(
        start=LocValue(pos=(3, 0), value=22, operator="", direction="", last_pos=None)
    )
    result = bfs(initial=cave, goal_test=Cave.goal_test, successors=Cave.successors)

    if result is not None:
        for index, itm in enumerate(node_to_path(result)):
            x, y = itm.state.pos
            print(
                itm.state.direction,
                # f"{itm.board[x][y]}",
            )
    else:
        print("no Result")

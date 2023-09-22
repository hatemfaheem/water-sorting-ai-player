import copy
from dataclasses import dataclass
from heapq import heappush, heappop
from typing import List, Optional


@dataclass
class Solution:
    is_solved: bool
    solution_steps: Optional[List[tuple[int, int]]]


class Solver:
    def __init__(self, debug_mode: bool) -> None:
        self.debug_mode = debug_mode

    def solve_level(self, start_state: List[List[int]]):
        """
        :param start_state: list of lists of color indexes including empty arrays at the end for empty tubes.
        :return: a solution object for this level.
        """
        queue = []
        heappush(queue, (0, start_state, None, None))
        visited = set(str(start_state))
        solved = False
        goal_state = None
        while len(queue) > 0:
            top_state = heappop(queue)
            self._render(top_state[1])
            if self._is_goal(top_state[1]):
                solved = True
                goal_state = top_state
                break
            count_steps = self._next_steps(top_state, queue, visited)
            if self.debug_mode:
                print("heuristic:", top_state[0], "next_steps:", count_steps, "visited:", len(visited))

        if solved:
            path = self._generate_path(goal_state)
            return Solution(is_solved=True, solution_steps=path)

        if self.debug_mode:
            print("No solution found")
        return Solution(is_solved=False, solution_steps=None)

    def _render(self, state):
        if self.debug_mode:
            print("------------")
            for s in state:
                print(s)
            print("------------")

    @staticmethod
    def _is_tube_sorted(tube):
        if len(tube) == 0:  # Empty tube is OK
            return True
        if len(tube) != 4:  # Non-complete tube is NOT OK
            return False
        return len(set(tube)) == 1  # All colors in the tube are same

    def _is_goal(self, state):
        # This is the goal state only if all tubes are sorted.
        return all([self._is_tube_sorted(tube) for tube in state])

    @staticmethod
    def _can_spill(tube1, tube2):
        """
        Can we move contents from tube1 to tube2
        """
        if len(tube1) == 0:  # First tube is empty (Nothing to move)
            return False
        if len(tube2) == 0:  # Second tube is empty (Anything can be moved)
            return True

        # Tube 2 is not full AND top color tube 1 is same as top color of tube 2
        if len(tube2) < 4 and tube1[0] == tube2[0]:
            return True

        return False

    @staticmethod
    def _spill(tube1, tube2):
        # Move contents from tube 1 to tube 2
        # As long as tube 1 top color is the same, tube 1 is not empty and tub 2 is not full.
        while len(tube1) > 0 and len(tube2) < 4 and (len(tube2) == 0 or tube1[0] == tube2[0]):
            tube2.insert(0, tube1[0])
            tube1.pop(0)

    @staticmethod
    def _heuristic(state):
        """
        The more complete (or closer to complete) tubes the state has, the better (lower hueristic).
        """
        score = 0
        for tube in state:
            if len(tube) == 4 and len(set(tube)) == 1:
                score -= 10
            elif len(tube) == 3 and len(set(tube)) == 1:
                score -= 5
            elif len(tube) == 3 and (tube[0] == tube[1] or tube[1] == tube[2]):
                score -= 2
            elif len(tube) == 2 and tube[0] == tube[1]:
                score -= 2
        return score

    def _next_steps(self, state_obj, queue, visited):
        """
        Generate all next possible states as long as they haven't been visited before.
        """
        state = state_obj[1]
        count_steps = 0
        for i in range(len(state)):
            for j in range(len(state)):
                if i != j and self._can_spill(state[i], state[j]):
                    new_state = copy.deepcopy(state)
                    self._spill(new_state[i], new_state[j])
                    if not str(new_state) in visited:
                        visited.add(str(new_state))
                        heappush(queue, (self._heuristic(new_state), new_state, state_obj, (i, j)))
                        count_steps += 1
        return count_steps

    @staticmethod
    def _generate_path(goal_state) -> List[tuple[int, int]]:
        """
        Generate final path by looking backwards from the goal state.
        goal state -> before goal -> before before goal -> .... -> initial state
        """
        path = [goal_state[3]]
        prev_state = goal_state[2]
        while prev_state is not None and prev_state[2] is not None:
            path.append(prev_state[3])
            prev_state = prev_state[2]

        # Reverse the path to get the final answer
        # initial state -> second state -> ... -> goal state
        return path[::-1]

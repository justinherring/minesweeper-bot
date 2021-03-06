#!/usr/bin/env python3

from collections import deque
from copy import deepcopy

import colorama

# Use Python to solve a Minesweeper board!
# The brains of the operation

# ? if unloaded
# _ if unknown
# 0-8 for how many bombs are known to be around
# F for flagged bomb
# * for found bomb (i.e., game over)

class Puzzle:
    
    def __init__(self, width=30, height=16, number_bombs=99):
        self.width = width
        self.height = height
        self.bombs = number_bombs
        self.flags = 0
        self.board = [["?" for _ in range(self.width)] for __ in range(self.height)]
        self._old_board = [["?" for _ in range(self.width)] for __ in range(self.height)]
    
    # loads a new board
    def load_board(self, board):
        self._old_board = deepcopy(self.board)
        self.board = board
        number_flags = 0
        for row in board:
            for col in row:
                if col == "F":
                    number_flags += 1
        self.flags = number_flags
    
    # prints the board
    def print(self):
        colorama.init()
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == "*":
                    print(colorama.Fore.RED + self.board[y][x] + colorama.Fore.RESET, end=" ")
                elif self.board[y][x] == "f":
                    print(colorama.Back.RED + self.board[y][x] + colorama.Back.RESET, end=" ")
                elif self.board[y][x] != self._old_board[y][x]:
                    print(colorama.Back.GREEN + self.board[y][x], end=" " + colorama.Back.RESET)
                else:
                    print(self.board[y][x], end=" ")
            print()
        colorama.deinit()


    # returns true if game is over (i.e., bomb is revealed)
    def is_over(self):
        for row in self.board:
            for col in row:
                if col == "*":
                    return True
        return False

    # returns the content of the board at (x,y) as well as (x,y)
    def content_and_coord(self, x, y):
        assert 0 <= x < self.width, "x=%d is out of bounds" % x
        assert 0 <= y < self.height, "y=%d is out of bounds" % y
        return (self.board[y][x], (x, y))

    # returns the content and coordinates of all valid adjacent tiles to (x,y) 
    def _adjacent_tiles_contain(self, x, y):
        adj_tiles = []
        if 0 < x <= self.width-1 and 0 <= y <= self.height-1:
            adj_tiles.append(self.content_and_coord(x-1, y))

        if 0 < x <= self.width-1 and 0 < y <= self.height-1:
            adj_tiles.append(self.content_and_coord(x-1, y-1))

        if 0 <= x <= self.width-1 and 0 < y <= self.height-1:
            adj_tiles.append(self.content_and_coord(x, y-1))

        if 0 <= x < self.width-1 and 0 < y <= self.height-1:
            adj_tiles.append(self.content_and_coord(x+1, y-1)) 

        if 0 <= x < self.width-1 and 0 <= y <= self.height-1:
            adj_tiles.append(self.content_and_coord(x+1, y))

        if 0 <= x < self.width-1 and 0 <= y < self.height-1:
            adj_tiles.append(self.content_and_coord(x+1, y+1))

        if 0 <= x <= self.width-1 and 0 <= y < self.height-1:
            adj_tiles.append(self.content_and_coord(x, y+1))

        if 0 < x <= self.width-1 and 0 <= y < self.height-1:
            adj_tiles.append(self.content_and_coord(x-1, y+1))

        return adj_tiles

    # returns the count and positions of tiles adjacent to tile (x,y) filled with symbol (e.g., "F" or "_") 
    def _adjacent_tiles_with(self, x, y, symbol="_"):
        adj = self._adjacent_tiles_contain(x, y)
        blanks = []
        count = 0
        for a in adj:
            if a[0] == symbol:
                count += 1
                blanks.append(a[1])
        return count, blanks

    # returns true if tile is on the frontier (i.e., neighboring unknown square and are 1-8)
    def _is_on_frontier(self, x, y):
        adj = self._adjacent_tiles_contain(x, y)
        isNeighboringUnknown = False
        for i in adj:
            if i[0] == "_":
                isNeighboringUnknown = True
        board_char = self.board[y][x]
        return not (board_char == "_" or board_char == "F" or board_char == "*") and isNeighboringUnknown

    # returns all 1-8 tiles that are neighboring unknown squares 
    def _frontier(self):
        # search space is 30 * 16 = 480 so we can just brute force
        frontier = []
        for y in range(self.height):
            for x in range(self.width):
                if self._is_on_frontier(x, y):
                    frontier.append((x, y))

        return frontier
        
    # returns positions of all unmarked flags on the frontier for tiles that 
    # have the same number as the amount of blank spaces by them 
    # FIXME: have to count flags that already exist as well
    def _easy_flags(self):
        frontier = self._frontier()
        q = deque()
        new_flags = set()

        # enqueue everything
        for f in frontier:
            q.append(f)

        # dequeue and check if anything can be easyflagged
        while len(q) > 0:
            x, y = q.popleft()
            # if it can be easy flagged, add to new_flag set and enqueue all neighbors
            # that are on the frontier
            blank_count, blanks = self._adjacent_tiles_with(x, y, "_")
            flag_count, flags = self._adjacent_tiles_with(x, y, "F")
            if str(blank_count-flag_count) == self.board[y][x]:
                new_info = False
                for b in blanks:
                    if b not in new_flags:
                        new_flags.add(b)
                        new_info = True
                if new_info:
                    adj = self._adjacent_tiles_contain(x, y)
                    for a in adj:
                        q.append(a[1])
        
        return new_flags

    def _mark_easy_flags(self):
        easy_flags = self._easy_flags()
        for x, y in easy_flags:
            self.board[y][x] = "F"
        return easy_flags
    
    # returns positions for all tiles that can be revealed given
    # a tile on the frontier has sufficient adjacent flags
    def _easy_reveals(self):
        frontier = self._frontier()
        q = deque()
        reveals = set()

        # enqueue frontier
        for f in frontier:
            q.append(f)
        
        # dequeue and check if tile's number matches how many flags there
        # if equal, then reveal every adjacent unknown tile
        while len(q) > 0:
            x, y = q.popleft()

            flag_count, flags = self._adjacent_tiles_with(x, y, "F")
            blank_count, blanks = self._adjacent_tiles_with(x, y, "_")
            if str(flag_count) == self.board[y][x]:
                for fx, fy in blanks:
                    if self.board[fy][fx] == "_" and (fx, fy) not in reveals:
                        reveals.add((fx, fy))

        return reveals

    # generates a list of next moves given current board state
    def next_move(self):
        pass
        

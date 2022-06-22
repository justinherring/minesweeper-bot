#!/usr/bin/env python3

# Use Python to solve a Minesweeper board!
# Using the board class to play online

from asyncore import read
from re import search
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from bs4 import BeautifulSoup

import minesweeper_board

def setup():
    # https://github.com/SergeyPirogov/webdriver_manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
    print()
    return driver


def print_board(board):
    for row in board:
        for col in row:
            print(col, end=" ")
        print()


def make_board(elems):
    board = [["?" for __ in range(30)] for _ in range(16)]
    
    for tag in elems:
        tagId = tag['id']
        y, x = [int(x)-1 for x in tagId.split("_")]
        if 0 <= y <= 15 and 0 <= x <= 29:
            if "blank" in tag["class"]:
                board[y][x] = "_"
            elif "open" in tag["class"][1]:
                # print("class is", tag["class"])
                board[y][x] = search("[0-9]", tag["class"][1]).group()
            elif "bombmisflagged" in tag["class"][1]:
                board[y][x] = "f"
            elif "flag" in tag["class"][1]:
                board[y][x] = "F"
            elif "bomb" in tag["class"][1]:
                board[y][x] = "*"
    
    return board


def main():
    driver = setup()
    driver.get("https://minesweeperonline.com/")

    def left_click(x, y):
        driver.find_element(By.ID, f"{y+1}_{x+1}").click()
    
    def right_click(x, y):
        square = driver.find_element(By.ID, f"{y+1}_{x+1}")
        ActionChains(driver).context_click(square).perform()
    
    puzzle = minesweeper_board.Puzzle()
    
    def read_and_load():
        src = BeautifulSoup(driver.page_source, "lxml")
        squares = src.find_all(class_="square")
        board = make_board(squares)
        puzzle.load_board(board)
    
    left_click(randint(0, 29), randint(0, 15))

    read_and_load()
    print("step #0")
    puzzle.print()

    newFlags = True
    newReveals = True
    current_step = 1
    while (newFlags or newReveals) and not puzzle.is_over():
        read_and_load()

        easy_flags = puzzle._mark_easy_flags()
        newFlags = (easy_flags != set())
        for x, y in easy_flags:
            right_click(x, y)

        print(f"step #{current_step}")
        current_step += 1
        puzzle.print()

        read_and_load()

        easy_reveals = puzzle._easy_reveals()
        newReveals = (easy_reveals != set())
        for x, y in easy_reveals:
            left_click(x, y)

        print(f"step #{current_step}")
        current_step += 1
        puzzle.print()


    driver.quit()    

    
if __name__ == "__main__":
    main()

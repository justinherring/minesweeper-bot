#!/usr/bin/env python3

# Use Python to solve a Minesweeper board!

from re import search

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from bs4 import BeautifulSoup

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
        y, x = [int(x) for x in tagId.split("_")]
        if 1 <= y <= 16 and 1 <= x <= 30:
            if "blank" in tag["class"]:
                board[y-1][x-1] = "_"
            elif "open" in tag["class"][1]:
                # print("class is", tag["class"])
                board[y-1][x-1] = search("[0-9]", tag["class"][1]).group()
    
    print_board(board)



def main():
    driver = setup()
    driver.get("https://minesweeperonline.com/")
    
    src = BeautifulSoup(driver.page_source, "lxml")
    squares = src.find_all(class_="square")
    make_board(squares)
    print()

    driver.find_element(By.ID, "7_19").click()

    src = BeautifulSoup(driver.page_source, "lxml")
    squares = src.find_all(class_="square")
    make_board(squares)


    driver.quit()    

    

if __name__ == "__main__":
    main()

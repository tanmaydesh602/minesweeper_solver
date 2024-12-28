import os
import pyautogui
from PIL import Image, ImageDraw
import random
import time 
import numpy as np
import cv2

# Initialize the game board array
cols = 24  # Number of columns in the board
rows = 20  # Number of rows in the board
speed = 0.05 # time between each move
board_array = [['?' for _ in range(cols)] for _ in range(rows)]

# Function to determine the tile's state based on its color
def getColor(color):
    r, g, b = color[:3]  # Extract only the first three values (R, G, B)

    # Match specific colors for numbers
    if 150 <= r <= 185 and 150 <= g <= 185 and 150 <= b <= 185:  # Blue
        return 1
    if 140 <= r <= 180 and 165 <= g <= 190 and 100 <= b <= 134:   # Green
        return 2
    if 190 <= r <= 225 and 130 <= g <= 160 and 100 <= b <= 135:   # Red
        return 3
    if 170 <= r <= 200 and 130 <= g <= 160 and 140 <= b <= 170: # Purple
        return 4
    if 200 <= r <= 240 and 155 <= g <= 185 and 85 <= b <= 120:  # Orange
        return 5
    if 0 <= r <= 30 and 240 <= g <= 260 and 240 <= b <= 266:  # Cyan
        return 6
    if 200 <= r <= 230 and 175 <= g <= 200 and 145 <= b <= 170: # No mine or number
        return 0
    return '?'  # unopened (unrevealed)

def load_board(left, top, right, bottom, tile_size):
    pyautogui.moveTo(left-5,top+5)
    screenshot = pyautogui.screenshot()
    board_image = screenshot.crop((left, top, right, bottom))
    save_path = "images/minesweeper_board.png"
    os.makedirs("images", exist_ok=True)
    board_image.save(save_path)
    pixel_data = board_image.load()
    for row in range(rows):
        for col in range(cols):
            if board_array[row][col] != 'F':
                # Define the middle 1/3 column boundaries of the current tile
                x_start = int(col * tile_size + tile_size / 3)
                x_end = int(col * tile_size + 2 * tile_size / 3)
                y_start = int(row * tile_size)
                y_end = int((row + 1) * tile_size)

                # Calculate the average color of the middle 1/3 column of the tile
                r_total, g_total, b_total, count = 0, 0, 0, 0
                for x in range(x_start, x_end):
                    for y in range(y_start, y_end):
                        if 0 <= x < board_image.width and 0 <= y < board_image.height:
                            r, g, b = pixel_data[x, y][:3]
                            r_total += r
                            g_total += g
                            b_total += b
                            count += 1

                avg_color = (r_total // count, g_total // count, b_total // count)
                tile_state = getColor(avg_color)
                board_array[row][col] = tile_state
                print(f"Tile ({row}, {col}): Avg Color = {avg_color}, State = {tile_state}")
    board_path = "images/game_board.txt"
    with open(board_path, "w") as f:
        for row in board_array:
            f.write(" ".join(map(str, row)) + "\n")
    print(f"Game board array saved to {board_path}")

def getNeighbors(col, row):    # return unknown neighbors
    res = []
    try:
        if col - 1 >= 0 and row - 1 >= 0 and board_array[col - 1][row - 1] == '?':
            res.append((col - 1, row - 1))
    except:
        pass
    try:
        if row - 1 >= 0 and board_array[col][row - 1] == '?':
            res.append((col, row - 1))
    except:
        pass
    try:
        if col + 1 < len(board_array) and row - 1 >= 0 and board_array[col + 1][row - 1] == '?':
            res.append((col + 1, row - 1))
    except:
        pass
    try:
        if col - 1 >= 0 and board_array[col - 1][row] == '?':
            res.append((col - 1, row))
    except:
        pass
    try:
        if col + 1 < len(board_array) and board_array[col + 1][row] == '?':
            res.append((col + 1, row))
    except:
        pass
    try:
        if col - 1 >= 0 and row + 1 < len(board_array[0]) and board_array[col - 1][row + 1] == '?':
            res.append((col - 1, row + 1))
    except:
        pass
    try:
        if row + 1 < len(board_array[0]) and board_array[col][row + 1] == '?':
            res.append((col, row + 1))
    except:
        pass
    try:
        if col + 1 < len(board_array) and row + 1 < len(board_array[0]) and board_array[col + 1][row + 1] == '?':
            res.append((col + 1, row + 1))
    except:
        pass
    return res

def getFlags(col, row):    # return flagged neighbors
    res = []
    try:
        if col - 1 >= 0 and row - 1 >= 0 and board_array[col - 1][row - 1] == 'F':
            res.append((col - 1, row - 1))
    except:
        pass
    try:
        if row - 1 >= 0 and board_array[col][row - 1] == 'F':
            res.append((col, row - 1))
    except:
        pass
    try:
        if col + 1 < len(board_array) and row - 1 >= 0 and board_array[col + 1][row - 1] == 'F':
            res.append((col + 1, row - 1))
    except:
        pass
    try:
        if col - 1 >= 0 and board_array[col - 1][row] == 'F':
            res.append((col - 1, row))
    except:
        pass
    try:
        if col + 1 < len(board_array) and board_array[col + 1][row] == 'F':
            res.append((col + 1, row))
    except:
        pass
    try:
        if col - 1 >= 0 and row + 1 < len(board_array[0]) and board_array[col - 1][row + 1] == 'F':
            res.append((col - 1, row + 1))
    except:
        pass
    try:
        if row + 1 < len(board_array[0]) and board_array[col][row + 1] == 'F':
            res.append((col, row + 1))
    except:
        pass
    try:
        if col + 1 < len(board_array) and row + 1 < len(board_array[0]) and board_array[col + 1][row + 1] == 'F':
            res.append((col + 1, row + 1))
    except:
        pass
    return res

def reveal_cell(row, col, left, top, tile_size):
    # Calculate the center of the tile
    x_tile = left + col * tile_size + tile_size / 2
    y_tile = top + row * tile_size + tile_size / 2

    # Move to the calculated position and click
    pyautogui.moveTo(x_tile, y_tile)
    pyautogui.click()
    print(f"Revealed cell at row {row}, col {col} (pixel: {x_tile}, {y_tile})")


def flag_cell(row,col,left,top,tile_size):
    board_array[row][col]='F'
    x_tile = left + col * tile_size + tile_size / 2
    y_tile = top + row * tile_size + tile_size / 2
    pyautogui.moveTo(x_tile,y_tile)
    pyautogui.rightClick()
    board_path = "images/game_board.txt"
    with open(board_path, "w") as f:
        for row in board_array:
            f.write(" ".join(map(str, row)) + "\n")

def selectCell(lastCell):
    col, th_x = lastCell[0], lastCell[0]
    row, th_y = lastCell[1], lastCell[1]
    dx = 0
    dy = -1
    cont = 0    # cells checked (in board)
    while cont < rows * cols:
        if col < cols and row < rows and col >= 0 and row >= 0:
            score = board_array[row][col]
            if score != 0 and score != 'F':
                try:
                    neighbors = getNeighbors(row,col)
                    flaggeds = getFlags(row,col)
                    if len(flaggeds) < int(score) and len(neighbors) + len(flaggeds) <= int(score):
                        return (neighbors, 0)    # select cells to place flag
                    elif len(flaggeds) == int(score) and len(neighbors) > 0:
                        return (neighbors, 1)    # select cells to click
                except:
                    pass
            cont += 1
        col -= th_x
        row -= th_y
        if col == row or (col < 0 and col == -row) or (col > 0 and col == 1 - row):
            dx, dy = -dy, dx
        col, row = col + dx + th_x, row + dy + th_y
    return (None, 2)    # select random cell to click

def main():
    input("Move the mouse to the TOP-LEFT corner of the board and hit Enter")
    left, top = pyautogui.position()
    input("Move the mouse to the BOTTOM-RIGHT corner of the board and hit Enter")
    right, bottom = pyautogui.position()

    tile_width = (right - left) / cols
    tile_height = (bottom - top) / rows
    tile_size = min(tile_width, tile_height) 
    print(f"Calculated tile size: {tile_size:.2f} pixels")

    load_board(left,top,right,bottom,tile_size)
    pyautogui.moveTo(left,top) #click into the game window
    pyautogui.click()

    reveal_cell(random.randint(0,rows-1),random.randint(0,cols-1),left,top,tile_size)#gotta start somewhere
    bombs = 99 #bombs
    lastCell = (0, 0)
    time.sleep(1)
    while(bombs>0):
        load_board(left,top,right,bottom,tile_size)
        cells, click = selectCell(lastCell)
        if click == 0:
            for cell in cells:
                flag_cell(cell[0],cell[1],left,top,tile_size)
                bombs -= 1
                lastCell = cell
        elif click == 1:
            for cell in cells:
                if cell[0]<0 or cell[1]<0:
                    print("uh oh errror")
                    return
                reveal_cell(cell[0],cell[1],left,top,tile_size)
                lastCell = cell
        elif click == 2:    # click random cell
            for row in range(0,rows):
                for col in range(0,cols):
                    if(board_array[row][col]=='?'):
                        reveal_cell(row,col,left,top,tile_size)
                else:
                    continue
                break
        time.sleep(speed)
    print("done")

if __name__ == "__main__":
    main()
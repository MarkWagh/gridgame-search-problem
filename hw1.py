import time
import numpy as np 
import random # importing Random to pick random color and shape (brush)
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.5, gs=10, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")


##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below. 
##########################################



# length of the grid numpy array
gs= len(grid)

# this is a list of brushes. I am using this instead of defining the entire list manually, to identify if a random brush chosen can be placed on the grid.
shapes = game.shapes #List of Numpy arrays of the brushes
num_shapes = len(shapes)


# this is my objective function, which is basically checking how many empty cells (-1) are present and if the grid color is matching the adjacent color. Lower the value of the objective funtion, the better! 0 being the ideal.
def objective(g):
    empty = np.sum(g == -1) #counts the total no. of empty cells -1.
    conflicts = 0
    for i in range(gs):
        for j in range(gs):
            if g[i,j] >= 0:
                # check the right neighbor if color matches
                if j < gs-1 and g[i,j] == g[i,j+1]:
                    conflicts += 1
                # check bottom neighbors color matches
                if i < gs-1 and g[i,j] == g[i+1,j]:
                    conflicts += 1
    return empty + conflicts * 10 #amplifying the conflicts because that is the main objective.

# this function is to simulate placing a shape without actually doing it & returning the new grid to calculate if the score has now improved or no.
def simulate_place(g, shape_idx, x, y, color):
    new_g = g.copy()
    shape = shapes[shape_idx]
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val:
                new_g[y + r, x + c] = color
    return new_g

# check if we can place shape at position 
def can_place(g, shape_idx, x, y):
    shape = shapes[shape_idx] #list of a numpy array [1,0][0,1]
    h, w = shape.shape #numpy array's shap attribut to read no. of row & col
    if x + w > gs or y + h > gs:
        return False
    
    #loop to check if the brush can be placed.
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val and g[y + r, x + c] != -1:
                return False
    return True

# move brush to target position
def move_to(target_x, target_y):
    global shapePos
    while shapePos[0] < target_x:
        shapePos, _, _, _, _, _ = game.execute('right')
    while shapePos[0] > target_x:
        shapePos, _, _, _, _, _ = game.execute('left')
    while shapePos[1] < target_y:
        shapePos, _, _, _, _, _ = game.execute('down')
    while shapePos[1] > target_y:
        shapePos, _, _, _, _, _ = game.execute('up')

# simple function to switch to target shape
def switch_shape(target):
    global currentShapeIndex, shapePos
    while currentShapeIndex != target:
        shapePos, currentShapeIndex, _, _, _, _ = game.execute('switchshape')

# simple funtion to switch to target color
def switch_color(target):
    global currentColorIndex
    while currentColorIndex != target:
        _, _, currentColorIndex, _, _, _ = game.execute('switchcolor')

# checking the objective function score empty cells + conflicts * 10
current_score = objective(grid)
no_improve = 0 # setting number of improvements
max_no_improve = 5000000  # maximum retries of improvements we can do, increase this for larger grid size.

# local search picking random move and evaluating it
while not done and no_improve < max_no_improve:
    # pick random shape, position, color

    shape_index = random.randint(1, num_shapes - 1) # assigning higher brushes for fewer shapes between 1-8
    dims = game.shapesDims[shape_index] # gives us the dimensions of eacd brush (2,2) (4,2)
    
    max_x = gs - dims[0] # can be placed at max which row cell
    max_y = gs - dims[1] #can be placed at max which col cell
    
    # skip if max row/col greater than grid size
    if max_x < 0 or max_y < 0:
        no_improve += 1
        continue
    
    # choose a random row/col to start from
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    # choosing a random color
    color = random.randint(0, 3)
    
    # check if placement of the brush is valid
    if not can_place(grid, shape_index, x, y):
        no_improve += 1
        continue
    
    # Simulate and check the objective 
    new_grid = simulate_place(grid, shape_index, x, y, color)
    new_score = objective(new_grid)
    
    # first choice: accept if better or equal, using sideways
    if new_score <= current_score:
        # execute the move
        switch_shape(shape_index)
        switch_color(color)
        move_to(x, y)
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('place')
        # print(grid)
        # print(done)
        if new_score < current_score:
            no_improve = 0
        else:
            no_improve += 1
        current_score = objective(grid)
    else:
        no_improve += 1

# if stuck, fill remaining cells one by one using getAvailableColor public function
if not done:
    switch_shape(0)  # use 1x1 brush
    for i in range(gs):
        for j in range(gs):
            if grid[i, j] == -1:
                # Get a color that won't conflict with neighbors
                color = game.getAvailableColor(grid, j, i)
                switch_color(color)
                move_to(j, i)
                shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('place')
                # print("Grid in the Fallback", grid)

                # print(done)
                if done:
                    break
        if done:
            break

print(grid, done)

########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
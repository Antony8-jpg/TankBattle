import pygame
import math
from queue import PriorityQueue

#import files
from Variabels import *
from ScreenObjects import *
from MovingObjects import *

class Grid:
    def screen_to_grid(pos): 
        return (int(pos.x) // grid_size, int(pos.y) // grid_size)

    def grid_to_screen(grid_pos):
        return pygame.math.Vector2((grid_pos[0] + 0.5) * grid_size, (grid_pos[1] + 0.5) * grid_size)

    def build_grid(): # maak een de map een grid van nullen en 1 , 0 als vrij en 1 als er een obstacle is
        grid = []
        for i in range(grid_length): # verandert elke cel in een 0 
            row = [0] * grid_height 
            grid.append(row)
    
        for obj in list_of_objects: # vervangt de 0 door een 1 als er een obstacle is
            if isinstance(obj, (Wall, Bush)):
                grid[obj.grid_x][obj.grid_y] = 1

        return grid
    
    def heuristic(a, b): #Manhatten distance tussen twee punten a an b
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clear_area(grid, x, y, clearance):  # om een vrije 3x3 gebied te vinden zodat de bot zeker door kan gaan (zou kunnen botsen tegen zijkant als 1x1)
        grid_width = len(grid)
        grid_height = len(grid[0])
        
        # gaat loopen over elke grid in nabijheid bot (3x3) als die vrij is of niet, clearance zal =1 zijn bij oproepen van functie
        for dx in range(-clearance, clearance + 1):
            for dy in range(-clearance, clearance + 1):
                check_x = x + dx
                check_y = y + dy

                # overslaan als de cel buiten de grid is
                if check_x < 0 or check_x >= grid_width:
                    return False
                if check_y < 0 or check_y >= grid_height:
                    return False

                # checken als obstacle op de grid
                if grid[check_x][check_y] == 1:
                    return False

        # alle andere grids zijn dan vrij -> True
        return True

    def astar(start_cell, goal_cell, grid): 
        #priority queue aanmaken en start_cell toevoegen met priority 0
        open_cells = PriorityQueue()
        open_cells.put((0, start_cell))

        #dict om het pad bij te houden via backtracking 
        came_from = {}
        #de kost om van start tot huidige cell te gaan
        cost_from_start = {start_cell: 0}

        #loopen over alle open cellen
        while not open_cells.empty():
            #beginnen met de cell met de kleinste estimated_total_cost
            current_priority, current_cell = open_cells.get()

            #doel bereikt -> maak het pad via backtracking
            if current_cell == goal_cell:
                path = []
                while current_cell in came_from:
                    path.append(current_cell)
                    current_cell = came_from[current_cell]
                path.reverse() #pad moet nog omgedraaid worden
                return path

            #alle mogelijke richtingen: horizontaal, verticaal en diagonaal
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction_x, direction_y in directions:
                neighbour_x = current_cell[0] + direction_x
                neighbour_y = current_cell[1] + direction_y
                neighbour_cell = (neighbour_x, neighbour_y)

                #begin opnieuw als de cel buiten het veld is
                if neighbour_x < 0 or neighbour_x >= grid_length:
                    continue
                if neighbour_y < 0 or neighbour_y >= grid_height:
                    continue

                #begin opnieuw als de cel ernaast niet vrij is
                is_walkable = Grid.clear_area(grid, neighbour_x, neighbour_y, clearance=1)
                if not is_walkable:
                    continue
                
                #voorkomen dat je diagonaal door obstakels gaat, dit deel komt van chatgpt
                if abs(direction_x) == 1 and abs(direction_y) == 1: #bijvoorbeeld van positie (3,3) naar (4,4)
                    adj1_x, adj1_y = neighbour_x, current_cell[1]  #horizontaal vakje ernaast
                    adj2_x, adj2_y = current_cell[0], neighbour_y  #verticaal vakje ernaast

                    if (0 <= adj1_x < grid_length and 0 <= adj1_y < grid_height and #controleerd of vakjes ernaast in de grid liggen
                        0 <= adj2_x < grid_length and 0 <= adj2_y < grid_height):

                        if grid[adj1_x][adj1_y] == 1 or grid[adj2_x][adj2_y] == 1:
                            continue  

                #de kost van de stap bepalen: 1 voor recht, sqrt(2) voor diagonaal en de kost updaten
                step_cost = math.sqrt(2) if abs(direction_x) + abs(direction_y) == 2 else 1
                # step_cost = 1 if abs(direction_x) + abs(direction_y) == 2 else math.sqrt(2)

                new_cost = cost_from_start[current_cell] + step_cost

                #als deze route goedkoper is dan een eerder gevonden pad naar deze cel
                if neighbour_cell not in cost_from_start or new_cost < cost_from_start[neighbour_cell]:
                    came_from[neighbour_cell] = current_cell #update het pad
                    cost_from_start[neighbour_cell] = new_cost #kost van het pad updaten

                    #Bereken de prioriteit met behulp van de manhatten distance en voeg toe aan de queue
                    priority = new_cost + Grid.heuristic(neighbour_cell, goal_cell)
                    open_cells.put((priority, neighbour_cell))

        #Indien geen pad gevonden wordt 
        return None

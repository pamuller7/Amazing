*This project has been created as part of the 42 curriculum by Acercy, Pamuller*

# A-Maze-Ing

## Task distribution

🟨 = Debug, checking/fixing

✅ = main part

|  Files | Acercy | Pamuller |
|:-------|:------:|:--------:|
|find_way.py||✅||
|graphics.py|✅|||
|maze_checker.py||✅||
|parse.py|✅||
|vector2.py|✅||
|maze.py|🟨|✅||
|brutal_path.py||✅|
|kruskal.py|✅|||
|main.py|✅|🟨|


## Description

A-Maze-ing is a maze generator in Python, That requires a default configuration file to create a maze, and writes in a file -mentionned by the configration- the hexadecimal value of each walls, the entry and exit position and the procedure to find the shortest path.

two type of mazes can be generated:
- perfect: A maze is perfect if there is only one path between a position and an other. other are dead ends.
- unperfect: Multiple path to link the entry to the exit. 

### How to read the output file

```
Example output.txt for a 10*10 maze
D17B955113
945287D686
EFBAAFFF83
BFC4057FAA
AFFFAFFFAE
ABBFAFD543
C2AFAFFFD2
D2812B9112
BAA82C682A
C46EC556EE

Entry: (9, 9)
Exit: (0, 0)
NNWSWSWWWNNNNNNWNNWWNW
```
Each cell of the maze is represented with binary values:
|binary value|1st byte|2nb byte|3rd byte|4th byte|
|:----------:|:------:|:------:|:------:|:------:|
|0|open north|open east|open south|open west|
|1|close north|close east|close south|close west|


which means that if the cell is 1100 (open to east and north), its value in base 10 will be 12, so C in hexadecimal.

F is 15 in base 10, so 1111 in binary, wich mean every walls are closed. You can see the 42 pattern in the example file.

The last line of the example are the directions to follow to go to the exit from the entry.
- N for north
- S for west
- E for east
- W for west

### Kurskal algo

### Brutal
The procedure here is simpler. We start for a random position in the maze and draw a random path, breaking through the unexplored cells, until it's in a dead end (sourrounded by the mazes limite or an other path), and repeat the execution for every incomplete cells.
this guarantees a perfect maze, as every path are dead ends, linked together (think it as a tree).
This one is a bit slower than the kurskal but patterns are different, and corridors are longer.

To create an imperfect maze, the only thing we have to do is once we encounter a dead end, we break a wall opening the new path to an other corridor -if existing-.

### Find_way
To find the shortest way, we use the Dijkstra method.
the idea is to calculate from each cell its distance from the exit.
the maze:
```
maze:		|	it's Dijkstra equivalent:
_________	|	_________
|I|___  |	|	|0 9 8 7|
|___  |	|	|	|1 2 3 6|
| __| __| 	|	|8 9 4 5|
|______O|	|	|7_6_5_6|


Here, to link I to O, it will take 6 mooves.
```

If this one is less faster than the a*, it's still interesting because after we have calculated once the Dijkstra tab, we know every distance from every cell to the exit.

## Instructions

### How to run
```
make run
```


### How to reuse the package
```
from mazegen.maze import Maze
from mazegen.parse import CheckedConfig
from mazegen.find_way import SolveMaze 
conf = {											
            "width": 20,								|
            "height": 20,								|
            "entry": (9, 9),							|
            "exit": (0, 0),								| a dict stocking the mandatory informations. careful, here the flag interactive will not be detected
            "output_file": "output_maze.txt",			|
            "perfect": True,							|
            "alt": True,								|
            "animate_generation": False,				|
            "theme": "red"								|
}													
conf = CheckedConfig(**conf)							| CheckedConfig checks if the keys are valid and returns a checkedconfig object, necessary for maze.
generated_maze = Maze(conf)								| generated_maze is the object stocking all the generated maze (generated_maze.maze will be the binary maze)
generated_maze.print_maze()

proc = SolveMaze(generated_maze).output_shortest_way()	| Once the maze is initialised, output shortest way will return the directions you must follow to get from entry to exit
print(proc)

```


### Config Text


The config text (its name doesn't matter as long as it's given as arguments) should at least contain the mandatory flags for the program to work.
```
==================================PROGRAMS MANDATORY==================================
WIDTH: an int between 0 and 1000
HEIGHT: an int between 0 and 1000 
ENTRY: coord (x,y) of the entry
EXIT: coord (x,y) of the exit
OUTPUT_FILE: file name of the file containing the hexa maze and the shortest way to link entry to exit
PERFECT: bool, saying if the maze should be perfect or not

===============================PROGRAMS FACULTATIVE FLAGS===============================
SEED: int, the seed for random, to generate the same maze
ANIMATE_GENERATION: bool (Default False), if you want the animation of the maze generation
ANIMATE_SHORTEST_WAY: bool (Default False), if you want the animation of the path finding
INTERACTIVE: bool (Default False), if you want the interactive interface
THEME: str (Default squeleton), for choosing a color theme for the output themes available: red, squeleton, rgb, green
DRAWING: str (Default 42), to choose a different drawing in the maze drawings available: 42, smiley, pac-man, no_drawing
```
INTERACTIVE = main only


### additional features


## Resources

Kurskal : https://fr.wikipedia.org/wiki/Algorithme_de_Kruskal

Dijkstra : https://fr.wikipedia.org/wiki/Algorithme_de_Dijkstra

AI used mostly for the building prompt: 
- peotry run commade
- ./venv/bin/python3 -m poetry install [Errno 2] No such file or directory: 'python'
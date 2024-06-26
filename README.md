<div align="center">

# Hide and Seek

### A theoretical game of Hide and Seek done by (hopefully) intelligent agents

</div>

## Motivation

Originally, this was done for a project due in a course of Artificial Intelligence. But as I do it, I feel like it's not a fun project to work on. So I deviated and started to redesign the project to be more fun and interesting. Starting the project, I had a goal in mind: to make this as a learning opportunity, and using what I studied in AIMA (Artificial Intelligence: A Modern Approach).

The original project requirements is [here](./docs/original.md).

## Overview

This project is a simulation of a game of Hide and Seek, where the hiders and seekers are intelligent agents. The hiders are tasked with hiding in the environment, while the seekers are tasked with finding the hiders. Only 1 seeker, though.

Project Structure Overview:

```
.
|-- src
    |-- agent.py
    |-- hide_and_seek.py
    |-- hider.py
    |-- seeker.py
    |-- map_state.py
    |-- vector2d.py
    |-- main.py
|-- maps
    |-- lX_mY.txt
    |-- ...
```

Where:

- `agent.py` contains the base class for an agent, including the moveset and vision.
- `hide_and_seek.py` contains the board, manages the positions for agents, can check whether the game is over.
- `hider.py` contains the hider class, which is a subclass of the agent class. Contains some additional methods for the hider.
- `seeker.py` contains the seeker class, which is a subclass of the agent class. Contains some additional methods for the seeker.
- `map_state.py` contains the map state class, which is a representation of the map itself.
- `vector2d.py` contains the `vector` class and `vectorf` class, which are basically tuples of 2 integers and 2 floats, respectively. The integer version is used for each cell in the map, while the float version is used for calculating raytracing.

## Structural Integrity

The map files are stored in the `maps/lX_mY.txt` directories (`X` being the target level and `Y` is the number of the map, this does not serve any purpose, just to split into levels and maps). It follows a common format:

```
<TIME>
<SEEKER_VISION> <SEEKER_MAX_STEP>
<HIDER_VISION> <HIDER_MAX_STEP>
<MAP>
```

Where:

- `<TIME>` is the time limit for seekers. Put a LARGE number for unlimited time (`int`).
- `<SEEKER_VISION>` is the vision of the seeker (`int`).
- `<SEEKER_MAX_STEP>` is the maximum number of steps the seeker can take (`int`).
- `<HIDER_VISION>` is the vision of the hider (`int`).
- `<HIDER_MAX_STEP>` is the maximum number of steps the hider can take (`int`).
- `<MAP>` is the map itself, where:
  - `.` is an empty space.
  - `H` is a hider.
  - `S` is a seeker.
  - `X` is a _immovable_ wall.
  - `B` is a _movable_ box.

<details>

<summary>Example Map</summary>

```
1000000000
3 1
0 0
.........................
................XX.......
................X........
..........X...X.X.XXXXXXX
..........X...X..........
XXXXXXXX..X...X..........
..........X...XXX........
...S......X.....X........
..........X.....X........
................X.......H
```

This map has a time limit of `1000000000`, a seeker vision of `3`, a seeker max step of `1`, a hider vision of `0`, and a hider max step of `0`. The map is a 10x25 grid. All `.` cells are _traversable_.

</details>

## The Game

The game is a simple simulation of states. The game is played in a 2D grid, where the agents can move in 8 directions (up, down, left, right, and diagonals). The agents have a vision range, which is the number of squares they can see around themselves. The agents can only see in a square around themselves, and they can only see the _current_ state of the map, **without** knowing about opponents.

The game is played accordingly:

1. Check if the game is over (time limit reached, or all hiders caught). If it is over, go to step 6.
2. Tick the seeker. The seeker looks around itself, updates its internal state, and moves.
3. Tick the game board. Check if the seeker overlaps _any_ hiders, if it does, the hider is caught. Update the game board accordingly.
4. Tick the hiders. The _remaining_ hiders look around themselves, update their internal state, and move (if possible).
5. The score and time is ticked. Score gets deducted by 1 for each step. Time gets incremented by 1 for each step. If the time limit is reached, the game is over. For each hider the seeker caught in this _tick_, the score gets increased by `20`.
6. Finished 1 state. Wait for next tick.

The game board is displayed with the following characters:

- `.` is an empty space.
- `H` is a hider.
- `S` is a seeker.
- `X` is a _immovable_ wall.
- `☐` is a _movable_ box.
- `-` is what the seeker can see.
- `*` is the _alert flare_.

## Seeker

- **Performance Measure**: catch _all_ hiders, in the fewest steps possible, within the time limit.
- **Environment**: a known map, with boxes and walls. Only us, the gamemasters, know where the hiders are.
- **Actuators**: the agent may move in any 8 directions, or stay in place (unlikely).
- **Sensors**: the agent can see in a square around itself, with a vision radius of `n` (where `n` is the _vision range_).

A step is defined as a movement in any of the 8 directions, or staying in place. The seeker goes through 2 stages: `perceive` and `accept`.

- **Perception**: The seeker looks around, and checks cells it _can see_ (not blocked), and are valid (not WALL, not BORDER). It may ask the gamemaster whether a cell has a hider or not. If the cell is _empty_, it _cools down_ the cell. If the cell has a hider, it _heats up_ the cell. If the cell is a hider, it heats up by A LOT. If there is a flare shot, a _region_ around the flare is _heated up_.
- **Action**: The seeker checks its current state (the heatmap), and selects all cells with the _highest_ value (aka the hottest cells). It then runs a _multi A\*_ search from its current position, finds the first goal cell it can discover, and returns a direction to move to that cell.

## Hider

### Level 1 - Level 2

- **Performance Measure**: hide from the seeker within the time limit.
- **Environment**: a known map, with boxes and walls. Only us, the gamemasters, know where the seeker is.
- **Actuators**: the agent may move in any 8 directions, or stay in place. Or additionally, the agent may **shoot a flare**.
- **Sensors**: the agent can see in a square around itself, with a vision radius of `n` (where `n` is the _vision range_). This is shorter than the seeker's vision.

These two levels are basically the same, with the only difference being the number of hiders. In level 1, there is only 1 hider, while in level 2, there are multiples.

![Demo](./docs/level2demo.gif)

### Level 3

- **Performance Measure**: hide from the seeker within the time limit.
- **Environment**: a known map, with boxes and walls. Only us, the gamemasters, know where the seeker is.
- **Actuators**: the agent may move in any 8 directions, or stay in place. Or additionally, the agent may **shoot a flare**. The agent may also **move**.
- **Sensors**: the agent can see in a square around itself, with a vision radius of `n` (where `n` is the _vision range_). This is shorter than the seeker's vision.

Assuming, with similar configurations, this means the hider is a reverse-seeker. It wants to move to the coldest place possible, where the heatmap starts out to be hot. This is probably not it, as if the hider wants to move the shortest path too, the chance of it colliding with the seeker is very high.

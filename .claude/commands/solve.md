# Solve Ribbit Puzzle

Solve a Ribbit word puzzle. The user will provide either:
1. A path to an existing puzzle file
2. A puzzle grid and connections to create a new puzzle file

## Instructions

1. If the user provides a puzzle file path, run the solver directly:
   ```
   uv run python main.py <puzzle_file>
   ```

2. If the user provides a grid and connections (or an image), create a puzzle file first:
   - Create a `.txt` file with the grid and connections
   - Format:
     ```
     ABCD
     EFGH
     IJKL
     MNOP

     Connections:
     0-1
     1-2
     ...
     ```
   - Node numbering is 0-indexed, left-to-right, top-to-bottom
   - Use `-` or `.` for empty cells
   - Then run the solver on the created file

3. Display the results to the user, reporting all words of length 4 and over (grouped by length).

## User input

$ARGUMENTS

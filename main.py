#!/usr/bin/env python3
"""
Ribbit Puzzle Solver - CLI Entry Point

Usage:
    uv run python main.py puzzle.txt
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from ribbit_solver import Solution, load_words_wordfreq


def parse_puzzle_text(
    text: str,
) -> Tuple[str, List[Tuple[int, int]], List[List[str]], dict]:
    """
    Parse puzzle text with format:

    ABCD
    EFGH
    IJKL
    MNOP

    Connections:
    0-1
    1-2
    ...

    Use `-` or `.` for empty cells in the grid.
    Node numbering is left-to-right, top-to-bottom (skipping empty cells).

    Returns:
        (letters, edges, grid, node_to_pos) tuple
    """
    lines = [line.rstrip() for line in text.strip().split("\n")]

    # Find the "Connections:" line
    connections_idx = None
    for i, line in enumerate(lines):
        if line.lower().startswith("connections"):
            connections_idx = i
            break

    if connections_idx is None:
        raise ValueError("Puzzle file must contain a 'Connections:' section")

    # Parse grid (everything before Connections:, skip comments and blank lines)
    grid_lines = [
        line
        for line in lines[:connections_idx]
        if line.strip() and not line.strip().startswith("#")
    ]

    # Build letter mapping: grid position -> letter (skipping empty cells)
    letters = []
    grid_pos_to_node = {}  # maps (row, col) to node index
    node_to_pos = {}  # maps node index to (row, col)
    node_idx = 0

    # Build 2D grid for display
    grid = []
    for row, line in enumerate(grid_lines):
        grid_row = []
        for col, char in enumerate(line):
            if char in "-._" or char.isspace():
                grid_row.append(None)
                continue
            grid_row.append(char.upper())
            grid_pos_to_node[(row, col)] = node_idx
            node_to_pos[node_idx] = (row, col)
            letters.append(char.upper())
            node_idx += 1
        grid.append(grid_row)

    letters_str = "".join(letters)

    # Parse edges (everything after Connections:)
    edges = []
    for line in lines[connections_idx + 1 :]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Support formats: "0-1", "0,1", "0 1"
        for sep in ["-", ",", " "]:
            if sep in line:
                parts = line.split(sep)
                if len(parts) == 2:
                    try:
                        u, v = int(parts[0].strip()), int(parts[1].strip())
                        edges.append((u, v))
                        break
                    except ValueError:
                        pass

    return letters_str, edges, grid, node_to_pos


def parse_puzzle_file(
    filepath: Path,
) -> Tuple[str, List[Tuple[int, int]], List[List[str]], dict]:
    """
    Parse a puzzle file. See parse_puzzle_text for format details.

    Returns:
        (letters, edges, grid, node_to_pos) tuple
    """
    text = filepath.read_text()
    return parse_puzzle_text(text)


def generate_grid_edges(
    rows: int, cols: int, node_positions: dict
) -> List[Tuple[int, int]]:
    """Generate standard 4-connected grid edges for existing nodes."""
    edges = []
    pos_to_node = {pos: idx for idx, pos in enumerate(sorted(node_positions.keys()))}

    for (row, col), node in pos_to_node.items():
        # Check right neighbor
        if (row, col + 1) in pos_to_node:
            edges.append((node, pos_to_node[(row, col + 1)]))
        # Check down neighbor
        if (row + 1, col) in pos_to_node:
            edges.append((node, pos_to_node[(row + 1, col)]))

    return edges


def display_puzzle(
    grid: List[List[str]], edges: List[Tuple[int, int]], node_to_pos: dict
) -> None:
    """Display an ASCII visualization of the puzzle grid with connections."""
    if not grid:
        return

    rows = len(grid)
    cols = max(len(row) for row in grid)

    # Build reverse mapping: (row, col) -> node
    pos_to_node = {pos: node for node, pos in node_to_pos.items()}

    # Build edge set for quick lookup (both directions)
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def has_edge(pos1, pos2):
        n1 = pos_to_node.get(pos1)
        n2 = pos_to_node.get(pos2)
        if n1 is None or n2 is None:
            return False
        return (n1, n2) in edge_set

    # Fixed width per cell: "X(00)" = 5, connector " -- " = 4, total = 9
    CELL = 9

    print("\nPuzzle Grid:")
    print()

    for row in range(rows):
        # Letter row
        line1 = []
        for col in range(cols):
            letter = grid[row][col] if col < len(grid[row]) else None
            node = pos_to_node.get((row, col))

            if letter and node is not None:
                cell = f"{letter}({node:2d})"
            else:
                cell = "     "

            if col < cols - 1:
                conn = " -- " if has_edge((row, col), (row, col + 1)) else "    "
                line1.append(cell + conn)
            else:
                line1.append(cell)

        print("".join(line1))

        # Connection row (vertical/diagonal)
        if row < rows - 1:
            line2 = list(" " * (CELL * cols))
            for col in range(cols):
                base = col * CELL  # start position of this cell

                if has_edge((row, col), (row + 1, col)):  # vertical
                    line2[base + 1] = "|"
                if has_edge((row, col), (row + 1, col + 1)):  # diagonal right
                    line2[base + 5] = "\\"
                if col > 0 and has_edge(
                    (row, col), (row + 1, col - 1)
                ):  # diagonal left
                    line2[base - 3] = "/"

            print("".join(line2))

    print()


def display_results(found_words: List[str]) -> None:
    """Display found words grouped by length."""
    print(f"\n{'=' * 60}")
    print(f"FOUND {len(found_words)} WORDS:")
    print(f"{'=' * 60}")

    if found_words:
        by_length = {}
        for w in found_words:
            by_length.setdefault(len(w), []).append(w)

        for length in sorted(by_length.keys()):
            words_of_len = by_length[length]
            print(f"\n{length}-letter words ({len(words_of_len)}):")
            for i in range(0, len(words_of_len), 5):
                print("  " + ", ".join(words_of_len[i : i + 5]))
    else:
        print("\nNo words found!")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Solve Ribbit word puzzles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example puzzle file format:

  ABCD
  EFGH
  IJKL
  MNOP

  Connections:
  0-1
  1-2
  2-3
  4-5
  ...

Node numbering is left-to-right, top-to-bottom (0-indexed).
Use '-' or '.' for empty cells in the grid.
        """,
    )
    parser.add_argument("puzzle", type=Path, help="Path to puzzle file")
    parser.add_argument(
        "--dict-size",
        type=int,
        default=200_000,
        help="Dictionary size - top N words (default: 200000)",
    )

    args = parser.parse_args()

    if not args.puzzle.exists():
        print(f"Error: File not found: {args.puzzle}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("RIBBIT PUZZLE SOLVER")
    print("=" * 60)

    # Parse puzzle file
    print(f"\nLoading puzzle from: {args.puzzle}")
    try:
        letters, edges, grid, node_to_pos = parse_puzzle_file(args.puzzle)
    except ValueError as e:
        print(f"Error parsing puzzle: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Letters: {letters}")
    print(f"  Nodes: {len(letters)}")
    print(f"  Edges: {len(edges)}")

    # Display puzzle visualization
    display_puzzle(grid, edges, node_to_pos)

    # Load dictionary
    print("\nLoading dictionary...")
    try:
        words = load_words_wordfreq(top_n=args.dict_size, min_len=4)
        print(f"  Loaded {len(words):,} words (min length 4)")
    except ImportError:
        print("  wordfreq not installed, run: uv add wordfreq")
        sys.exit(1)

    # Solve
    print("\nSolving...")
    sol = Solution()
    found_words = sol.findWordsOnGraph(
        letters=letters,
        edges=edges,
        words=words,
        min_len=4,
    )

    display_results(found_words)


if __name__ == "__main__":
    main()

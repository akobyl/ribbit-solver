"""Tests for main.py puzzle parsing and display functions."""

import io
import sys
import pytest

from main import parse_puzzle_text, display_puzzle


class TestParsePuzzleText:
    """Tests for parse_puzzle_text function."""

    def test_simple_2x2_grid(self):
        """Test parsing a simple 2x2 grid."""
        text = """
AB
CD

Connections:
0-1
2-3
0-2
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "ABCD"
        assert edges == [(0, 1), (2, 3), (0, 2)]
        assert grid == [["A", "B"], ["C", "D"]]
        assert node_to_pos == {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)}

    def test_grid_with_empty_cells(self):
        """Test parsing a grid with empty cells marked by -."""
        text = """
A-B
-C-
D-E

Connections:
0-1
1-2
2-3
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "ABCDE"
        assert edges == [(0, 1), (1, 2), (2, 3)]
        assert grid == [["A", None, "B"], [None, "C", None], ["D", None, "E"]]
        assert node_to_pos == {0: (0, 0), 1: (0, 2), 2: (1, 1), 3: (2, 0), 4: (2, 2)}

    def test_grid_with_dot_empty_cells(self):
        """Test parsing a grid with empty cells marked by ."""
        text = """
A.B
.C.

Connections:
0-1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "ABC"
        assert grid == [["A", None, "B"], [None, "C", None]]

    def test_grid_with_underscore_empty_cells(self):
        """Test parsing a grid with empty cells marked by _."""
        text = """
A_B

Connections:
0-1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "AB"
        assert grid == [["A", None, "B"]]

    def test_lowercase_letters_converted_to_uppercase(self):
        """Test that lowercase letters are converted to uppercase."""
        text = """
abc
def

Connections:
0-1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "ABCDEF"
        assert grid == [["A", "B", "C"], ["D", "E", "F"]]

    def test_comments_ignored(self):
        """Test that comment lines are ignored."""
        text = """
# This is a comment
AB
# Another comment
CD

Connections:
# Comment in connections section
0-1
# More comments
1-2
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "ABCD"
        assert edges == [(0, 1), (1, 2)]

    def test_comma_separated_edges(self):
        """Test parsing edges with comma separator."""
        text = """
AB

Connections:
0,1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert edges == [(0, 1)]

    def test_space_separated_edges(self):
        """Test parsing edges with space separator."""
        text = """
AB

Connections:
0 1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert edges == [(0, 1)]

    def test_connections_case_insensitive(self):
        """Test that 'Connections:' header is case insensitive."""
        text = """
AB

CONNECTIONS:
0-1
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert edges == [(0, 1)]

    def test_missing_connections_raises_error(self):
        """Test that missing Connections section raises ValueError."""
        text = """
AB
CD
"""
        with pytest.raises(ValueError, match="Connections"):
            parse_puzzle_text(text)

    def test_4x4_grid(self):
        """Test parsing a standard 4x4 grid."""
        text = """
RLOU
AJXS
EOYL
HENC

Connections:
0-1
1-2
2-3
"""
        letters, edges, grid, node_to_pos = parse_puzzle_text(text)

        assert letters == "RLOU" + "AJXS" + "EOYL" + "HENC"
        assert len(node_to_pos) == 16
        assert node_to_pos[0] == (0, 0)
        assert node_to_pos[15] == (3, 3)


class TestDisplayPuzzle:
    """Tests for display_puzzle function."""

    def test_empty_grid_no_output(self, capsys):
        """Test that empty grid produces no output."""
        display_puzzle([], [], {})
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_simple_2x2_grid_display(self, capsys):
        """Test display of a simple 2x2 grid with horizontal connection."""
        grid = [["A", "B"], ["C", "D"]]
        edges = [(0, 1)]  # A-B connected
        node_to_pos = {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)}

        display_puzzle(grid, edges, node_to_pos)
        captured = capsys.readouterr()

        assert "Puzzle Grid:" in captured.out
        assert "A( 0)" in captured.out
        assert "B( 1)" in captured.out
        assert "--" in captured.out  # horizontal connection

    def test_vertical_connection_display(self, capsys):
        """Test display shows vertical connections with |."""
        grid = [["A"], ["B"]]
        edges = [(0, 1)]  # A-B connected vertically
        node_to_pos = {0: (0, 0), 1: (1, 0)}

        display_puzzle(grid, edges, node_to_pos)
        captured = capsys.readouterr()

        assert "|" in captured.out  # vertical connection

    def test_no_connection_no_dashes(self, capsys):
        """Test that unconnected cells don't show connection markers."""
        grid = [["A", "B"]]
        edges = []  # no connections
        node_to_pos = {0: (0, 0), 1: (0, 1)}

        display_puzzle(grid, edges, node_to_pos)
        captured = capsys.readouterr()

        # Should have cells but no -- between them
        assert "A( 0)" in captured.out
        assert "B( 1)" in captured.out
        # Check there's no -- connection (just spaces between cells)
        lines = captured.out.split("\n")
        letter_line = [l for l in lines if "A( 0)" in l][0]
        # Between cells should be spaces, not --
        assert "A( 0)    B( 1)" in letter_line

    def test_grid_with_none_cells(self, capsys):
        """Test display handles None cells (empty positions)."""
        grid = [["A", None, "B"]]
        edges = []
        node_to_pos = {0: (0, 0), 1: (0, 2)}

        display_puzzle(grid, edges, node_to_pos)
        captured = capsys.readouterr()

        assert "A( 0)" in captured.out
        assert "B( 1)" in captured.out

# Ribbit Solver

Solves Ribbit word puzzles by finding all valid dictionary words that can be formed by traversing connected nodes.

## Usage

```bash
uv run python main.py puzzle.txt
```

## Puzzle File Format

```
RLOU
AJXS
EOYL
HENC

Connections:
0-1
1-2
2-3
4-5
```

- **Grid**: Letters arranged in rows (top section)
- **Connections**: Node pairs that are connected (bottom section)
- Use `-`, `.`, or `_` for empty cells
- Lines starting with `#` are comments
- Node numbering is 0-indexed, left-to-right, top-to-bottom

### Node Numbering

For a 4x4 grid:
```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

## Options

```
--dict-size N    Dictionary size (default: 200000)
```

## Claude Code Skill

This repo includes a Claude Code skill for solving puzzles directly from the CLI.

### Installation

Add this repo's commands to your Claude Code configuration:

```bash
# From this repo directory
claude config add commandPaths .claude/commands
```

Or add globally by editing `~/.claude/settings.json`:
```json
{
  "commandPaths": ["/path/to/ribbit-solver/.claude/commands"]
}
```

### Usage

```
/solve puzzle.txt
/solve dec25.txt
```

Or describe a puzzle and Claude will create the file and solve it.

## Requirements

- Python 3.10+
- wordfreq library (installed automatically via uv)

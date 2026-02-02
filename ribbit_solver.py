from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Optional


# ----------------------------
# Trie
# ----------------------------
@dataclass
class TrieNode:
    children: Dict[str, "TrieNode"]
    word: Optional[str] = None  # store full word at terminal for O(1) output

    def __init__(self) -> None:
        self.children = {}
        self.word = None


def build_trie(words: List[str]) -> TrieNode:
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, TrieNode())
        node.word = w
    return root


# ----------------------------
# Solver (LeetCode-style)
# ----------------------------
class Solution:
    def findWordsOnGraph(
        self,
        letters: str,
        edges: List[Tuple[int, int]],
        words: List[str],
        min_len: int = 4,
    ) -> List[str]:
        """
        Find dictionary words that can be formed by walking a simple path
        (no node reused) on an undirected graph.

        Args:
            letters: letters[i] is the single lowercase char at node i.
            edges: list of undirected edges (u, v).
            words: dictionary words (any case; we'll normalize).
            min_len: minimum word length (>= 4 per prompt).

        Returns:
            Sorted list of found words (unique).
        """
        n = len(letters)
        if n == 0:
            return []

        letters = letters.lower()

        # Build adjacency list
        adj: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            if 0 <= u < n and 0 <= v < n and u != v:
                adj[u].append(v)
                adj[v].append(u)

        # Bound the search by node count (simple paths only)
        max_len = n

        # Normalize + filter dictionary
        filtered: List[str] = []
        for w in words:
            w = w.strip().lower()
            if len(w) < min_len or len(w) > max_len:
                continue
            if not w.isalpha():
                continue
            filtered.append(w)

        if not filtered:
            return []

        # Build trie from filtered dictionary
        root = build_trie(filtered)

        found: Set[str] = set()
        visited = [False] * n

        def dfs(i: int, node: TrieNode) -> None:
            ch = letters[i]
            nxt = node.children.get(ch)
            if nxt is None:
                return

            visited[i] = True

            if nxt.word is not None:
                # We already enforced min_len when building the trie.
                found.add(nxt.word)
                # Optional: clear to avoid re-adding the same word many times.
                nxt.word = None

            for j in adj[i]:
                if not visited[j]:
                    dfs(j, nxt)

            visited[i] = False

            # Optional pruning: if this subtree is now dead, remove it.
            if nxt.word is None and not nxt.children:
                del node.children[ch]

        # Start DFS from each node
        for i in range(n):
            if letters[i] in root.children:
                dfs(i, root)

        return sorted(found)


# ----------------------------
# Optional: dictionary loader
# ----------------------------
def load_words_wordfreq(
    top_n: int = 200_000,
    min_len: int = 4,
) -> List[str]:
    """
    Convenience loader using wordfreq.
    pip install wordfreq
    """
    from wordfreq import top_n_list

    words = top_n_list("en", top_n)
    return [w for w in words if len(w) >= min_len and w.isalpha()]


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    # Example graph:
    # 0-a -- 1-b -- 2-c
    #  |      \
    #  3-d     4-e
    letters = "abcde"
    edges = [(0, 1), (1, 2), (0, 3), (1, 4)]
    words = ["abed", "aced", "bade", "abc", "ab", "bead"]

    sol = Solution()
    print(sol.findWordsOnGraph(letters, edges, words, min_len=4))
    # Output might include: ['abed', 'bead', 'bade'] depending on edges/letters

import random

SIZE = 4
WIN_TILE = 2048


class Board:
    def __init__(self, grid=None):
        """Create a board. Pass `grid` (4x4 list) to start from a known state
        (used by tests); otherwise start empty and spawn two tiles."""
        self.score = 0
        # Filled in by every move_* call so the Game layer can report on it.
        self.last_gain = 0
        self.last_merges = 0
        if grid is not None:
            self.grid = [row[:] for row in grid]
        else:
            self.grid = [[0] * SIZE for _ in range(SIZE)]
            self.add_random_tile()
            self.add_random_tile()

    def add_random_tile(self):
        empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 4 if random.random() < 0.1 else 2

    # ---- merge logic -------------------------------------------------
    @staticmethod
    def slide_line_info(line):
        """Slide/merge one line toward index 0.

        Returns (new_line, points_gained, merge_count). Each original tile
        takes part in at most one merge per call: a tile produced by a merge
        is never merged again in the same move.
        """
        values = [x for x in line if x]
        result = []
        points = 0
        merges = 0
        i = 0
        while i < len(values):
            if i + 1 < len(values) and values[i] == values[i + 1]:
                merged = values[i] * 2
                result.append(merged)
                points += merged
                merges += 1
                i += 2  # both source tiles are consumed
            else:
                result.append(values[i])
                i += 1
        return result + [0] * (SIZE - len(result)), points, merges

    @staticmethod
    def slide_line(line):
        """Backward-compatible wrapper returning only the new line."""
        return Board.slide_line_info(line)[0]

    # ---- moves -------------------------------------------------------
    def _apply(self, lines, reverse):
        """Slide each line (rows or columns, as lists), return new lines and
        accumulate gain/merges. `reverse` slides toward the end of the line."""
        new_lines = []
        gain = merges = 0
        for line in lines:
            src = line[::-1] if reverse else line
            out, pts, mrg = self.slide_line_info(src)
            new_lines.append(out[::-1] if reverse else out)
            gain += pts
            merges += mrg
        return new_lines, gain, merges

    def _finish(self, old_lines, new_lines, gain, merges):
        changed = old_lines != new_lines
        if changed:
            self.score += gain
            self.last_gain, self.last_merges = gain, merges
        else:
            self.last_gain = self.last_merges = 0
        return changed

    def _rows(self):
        return [row[:] for row in self.grid]

    def _cols(self):
        return [[self.grid[r][c] for r in range(SIZE)] for c in range(SIZE)]

    def _set_rows(self, rows):
        self.grid = [row[:] for row in rows]

    def _set_cols(self, cols):
        self.grid = [[cols[c][r] for c in range(SIZE)] for r in range(SIZE)]

    def move_left(self):
        old = self._rows()
        new, gain, merges = self._apply(old, reverse=False)
        if old != new:
            self._set_rows(new)
        return self._finish(old, new, gain, merges)

    def move_right(self):
        old = self._rows()
        new, gain, merges = self._apply(old, reverse=True)
        if old != new:
            self._set_rows(new)
        return self._finish(old, new, gain, merges)

    def move_up(self):
        old = self._cols()
        new, gain, merges = self._apply(old, reverse=False)
        if old != new:
            self._set_cols(new)
        return self._finish(old, new, gain, merges)

    def move_down(self):
        old = self._cols()
        new, gain, merges = self._apply(old, reverse=True)
        if old != new:
            self._set_cols(new)
        return self._finish(old, new, gain, merges)

    # ---- state queries / snapshots ----------------------------------
    def has_won(self):
        return any(x >= WIN_TILE for row in self.grid for x in row)

    def can_move(self):
        if any(0 in row for row in self.grid):
            return True
        for r in range(SIZE):
            for c in range(SIZE):
                if c + 1 < SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r + 1 < SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def snapshot(self):
        return [row[:] for row in self.grid], self.score

    def restore(self, snap):
        grid, score = snap
        self.grid = [row[:] for row in grid]
        self.score = score
        self.last_gain = self.last_merges = 0

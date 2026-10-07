from collections import namedtuple

from board import Board

# Action-level result of one command: one accepted move -> one MoveResult.
MoveResult = namedtuple("MoveResult", "moved merges points message")

VALID_MOVES = ("w", "a", "s", "d")


class Game:
    def __init__(self, board=None):
        self.board = board if board is not None else Board()
        self.best_score = 0
        self.history = []  # at most one snapshot: the state before the last move

    def display(self):
        print("\n" + "+------+------+------+------+")
        for row in self.board.grid:
            print("|" + "|".join(f"{x:^6}" if x else f"{' ':^6}" for x in row) + "|")
            print("+------+------+------+------+")
        print("Score:", self.board.score, " Best:", self.best_score)

    # ---- state checks -------------------------------------------------
    def is_won(self):
        return self.board.has_won()

    def is_over(self):
        return not self.board.can_move()

    # ---- actions ------------------------------------------------------
    def move(self, key):
        """Apply one move. A tile is spawned and a snapshot saved only if the
        board actually changed. Returns a MoveResult."""
        moves = {"a": self.board.move_left, "d": self.board.move_right,
                 "w": self.board.move_up, "s": self.board.move_down}
        if key not in moves:
            return MoveResult(False, 0, 0, "Use W/A/S/D.")
        snap = self.board.snapshot()
        if not moves[key]():
            return MoveResult(False, 0, 0, "Nothing moved - try another direction.")
        self.history = [snap]  # one-level undo
        merges, points = self.board.last_merges, self.board.last_gain
        self.board.add_random_tile()
        self.best_score = max(self.best_score, self.board.score)
        if merges:
            plural = "s" if merges != 1 else ""
            msg = f"Moved. {merges} merge{plural}, +{points} points."
        else:
            msg = "Moved. No merges."
        return MoveResult(True, merges, points, msg)

    def undo(self):
        """Reverse exactly one successful move (board + score). Does not spawn
        a tile and does not lower the best score. Returns True if undone."""
        if not self.history:
            return False
        self.board.restore(self.history.pop())
        return True

    def run(self):
        print("2048 - W/A/S/D to move, U to undo, Q to quit.")
        while True:
            self.display()
            if self.is_won():
                print("You reached 2048! You win.")
                return
            if self.is_over():
                print("No legal moves remain. Game over.")
                return
            try:
                key = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                return
            if key == "q":
                print("Thanks for playing.")
                return
            if key == "u":
                print("Undone." if self.undo() else "Nothing to undo.")
                continue
            if key not in VALID_MOVES:
                print("Use W/A/S/D.")
                continue
            print(self.move(key).message)

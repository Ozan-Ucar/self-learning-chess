class Move:
    def __init__(self, from_sq, to_sq, piece_type, captured_piece=None, promotion=None):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.piece_type = piece_type
        self.captured_piece = captured_piece
        self.promotion = promotion

    def __repr__(self):
        return f"Move({self.from_sq} -> {self.to_sq})"

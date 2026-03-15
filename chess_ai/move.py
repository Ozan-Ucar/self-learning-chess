class Move:
    def __init__(self, from_sq, to_sq, piece_type, captured_piece=None, promotion=None, is_castling=False, is_en_passant=False):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.piece_type = piece_type
        self.captured_piece = captured_piece
        self.promotion = promotion
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant

    def __repr__(self):
        return f"Move({self.from_sq} -> {self.to_sq})"

        
    def to_uci(self):
        # Convert internal square index to algebraic notation (e.g., e2e4)
        files = "abcdefgh"
        ranks = "12345678"
        
        f1, r1 = self.from_sq % 8, self.from_sq // 8
        f2, r2 = self.to_sq % 8, self.to_sq // 8
        
        uci_str = f"{files[f1]}{ranks[r1]}{files[f2]}{ranks[r2]}"
        
        # Add promotion piece if applicable
        if self.promotion is not None:
            # Piece.QUEEN is 4, ROOK is 3, BISHOP is 2, KNIGHT is 1
            # Simple fallback for now
            uci_str += "q" if self.promotion == 4 else "n" # Expand later
            
        return uci_str


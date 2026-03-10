from .constants import *

class Board:
    def __init__(self):
        # Bitboards for each piece type and color
        self.pieces = {
            Color.WHITE: [0] * 6,
            Color.BLACK: [0] * 6
        }
        self.turn = Color.WHITE
        self.reset_board()

    def reset_board(self):
        # Pawns
        self.pieces[Color.WHITE][Piece.PAWN] = RANK_2
        self.pieces[Color.BLACK][Piece.PAWN] = RANK_7

        # Knights
        self.pieces[Color.WHITE][Piece.KNIGHT] = 0x42
        self.pieces[Color.BLACK][Piece.KNIGHT] = 0x4200000000000000

        # Bishops
        self.pieces[Color.WHITE][Piece.BISHOP] = 0x24
        self.pieces[Color.BLACK][Piece.BISHOP] = 0x2400000000000000

        # Rooks
        self.pieces[Color.WHITE][Piece.ROOK] = 0x81
        self.pieces[Color.BLACK][Piece.ROOK] = 0x8100000000000000

        # Queens
        self.pieces[Color.WHITE][Piece.QUEEN] = 0x08
        self.pieces[Color.BLACK][Piece.QUEEN] = 0x0800000000000000

        # Kings
        self.pieces[Color.WHITE][Piece.KING] = 0x10
        self.pieces[Color.BLACK][Piece.KING] = 0x1000000000000000

    def get_occupancy(self, color=None):
        if color is not None:
            return sum(self.pieces[color])
        return sum(self.pieces[Color.WHITE]) | sum(self.pieces[Color.BLACK])

    def print_board(self):
        full_board = self.get_occupancy()
        for r in range(7, -1, -1):
            row_str = f"{r+1} "
            for f in range(8):
                idx = r * 8 + f
                mask = 1 << idx
                if full_board & mask:
                    row_str += "X "
                else:
                    row_str += ". "
            print(row_str)
        print("  a b c d e f g h")

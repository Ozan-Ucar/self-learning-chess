from .constants import Piece, Color

# Standard material weights (Simplified for now)
# TODO: Add Piece-Square Tables (PST) to encourage center control
PIECE_VALUES = {
    Piece.PAWN: 100,
    Piece.KNIGHT: 320,
    Piece.BISHOP: 330,
    Piece.ROOK: 500,
    Piece.QUEEN: 900,
    Piece.KING: 20000 
}

def evaluate_material(board):
    score = 0
    # TODO: Optimize this with bit-count instructions if possible
    for piece_type in Piece:
        white_count = bin(board.pieces[Color.WHITE][piece_type]).count('1')
        black_count = bin(board.pieces[Color.BLACK][piece_type]).count('1')
        
        score += (white_count - black_count) * PIECE_VALUES[piece_type]
    
    return score

def get_full_evaluation(board):
    # TODO: Add mobility scoring and king safety
    return evaluate_material(board)

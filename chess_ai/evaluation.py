from .constants import Piece, Color

# Standard material weights
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
    # Simple counting of set bits (popcount) multiplied by value
    for piece_type in Piece:
        white_count = bin(board.pieces[Color.WHITE][piece_type]).count('1')
        black_count = bin(board.pieces[Color.BLACK][piece_type]).count('1')
        
        score += (white_count - black_count) * PIECE_VALUES[piece_type]
    
    # Return positive for white advantage, negative for black
    return score

def get_full_evaluation(board):
    # This will later include positional tables, mobility, and the neural network
    return evaluate_material(board)

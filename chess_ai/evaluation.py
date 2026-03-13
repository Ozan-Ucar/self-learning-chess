from .constants import Piece, Color

# Piece-Square Tables to encourage positional play
# Higher values mean better positions for those pieces
PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

def evaluate_material(board):
    score = 0
    for piece_type in Piece:
        white_bits = board.pieces[Color.WHITE][piece_type]
        black_bits = board.pieces[Color.BLACK][piece_type]
        
        # Base material
        white_count = bin(white_bits).count('1')
        black_count = bin(black_bits).count('1')
        score += (white_count - black_count) * PIECE_VALUES[piece_type]
        
        # Positional bonus (PST)
        if piece_type == Piece.PAWN:
            for i in range(64):
                if white_bits & (1 << i): score += PAWN_PST[63-i]
                if black_bits & (1 << i): score -= PAWN_PST[i]
        elif piece_type == Piece.KNIGHT:
            for i in range(64):
                if white_bits & (1 << i): score += KNIGHT_PST[63-i]
                if black_bits & (1 << i): score -= KNIGHT_PST[i]
    
    return score

def get_full_evaluation(board):
    # TODO: Add mobility scoring and king safety
    return evaluate_material(board)

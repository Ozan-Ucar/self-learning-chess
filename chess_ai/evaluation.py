from .constants import Piece, Color

PIECE_VALUES = {
    Piece.PAWN: 100,
    Piece.KNIGHT: 320,
    Piece.BISHOP: 330,
    Piece.ROOK: 500,
    Piece.QUEEN: 900,
    Piece.KING: 20000 
}

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

BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_PST = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_PST = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
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
        pst = None
        if piece_type == Piece.PAWN: pst = PAWN_PST
        elif piece_type == Piece.KNIGHT: pst = KNIGHT_PST
        elif piece_type == Piece.BISHOP: pst = BISHOP_PST
        elif piece_type == Piece.ROOK: pst = ROOK_PST
        elif piece_type == Piece.QUEEN: pst = QUEEN_PST
        elif piece_type == Piece.KING: pst = KING_PST
        
        if pst:
            for i in range(64):
                if white_bits & (1 << i): score += pst[63-i]
                if black_bits & (1 << i): score -= pst[i]
    
    return score

def evaluate_center_control(board):
    # Bonus for occupying the central squares (d4, e4, d5, e5)
    center_mask = 0x0000001818000000
    score = 0
    white_occ = board.get_occupancy(Color.WHITE)
    black_occ = board.get_occupancy(Color.BLACK)
    
    score += bin(white_occ & center_mask).count('1') * 30
    score -= bin(black_occ & center_mask).count('1') * 30
    return score

def evaluate_mobility(board):
    # Reward having more legal moves (more options = better position)
    color = board.turn
    own_moves = len(board.get_legal_moves())
    
    # Temporarily flip turn to count opponent moves
    board.turn = 1 - color
    opp_moves = len(board.get_legal_moves())
    board.turn = color
    
    diff = own_moves - opp_moves
    return diff * 10 if color == Color.WHITE else diff * -10

# Neural network evaluation (lazy-loaded)
_nn_model = None
_nn_loaded = False

def _get_nn_model():
    global _nn_model, _nn_loaded
    if _nn_loaded:
        return _nn_model
    _nn_loaded = True
    try:
        import os
        if os.path.exists("chess_model.pth"):
            from .model import load_or_create_model
            _nn_model = load_or_create_model("chess_model.pth")
            _nn_model.eval()
    except Exception:
        _nn_model = None
    return _nn_model

def get_nn_evaluation(board):
    """Use the trained neural network to evaluate the position."""
    model = _get_nn_model()
    if model is None:
        return None
    
    import torch
    from .model import board_to_tensor
    
    with torch.no_grad():
        tensor = board_to_tensor(board).unsqueeze(0)
        prediction = model(tensor).item()
    
    # Model outputs 0.0-1.0 (black wins to white wins)
    # Scale to centipawn range for blending with handcrafted eval
    return (prediction - 0.5) * 2000

_eval_cache = {}

def get_full_evaluation(board):
    fen = board.get_fen()
    if fen in _eval_cache:
        return _eval_cache[fen]
        
    score = evaluate_material(board)
    score += evaluate_center_control(board)
    
    # Blend in NN evaluation if available (30% weight)
    nn_score = get_nn_evaluation(board)
    if nn_score is not None:
        score = int(score * 0.7 + nn_score * 0.3)
    
    _eval_cache[fen] = score
    # simple cache memory management
    if len(_eval_cache) > 50000:
        _eval_cache.clear()
        
    return score

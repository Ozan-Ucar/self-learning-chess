from .evaluation import get_full_evaluation

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return get_full_evaluation(board)

    legal_moves = board.get_legal_moves()
    # Basic move ordering: check captures first
    legal_moves.sort(key=lambda m: m.captured_piece is not None, reverse=True)
    
    if not legal_moves:
        if board.is_in_check(board.turn):
            # Checkmate: negative infinity for the side in check
            return -100000 if maximizing_player else 100000
        return 0 # Stalemate

    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.unmake_move(move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.unmake_move(move)
            min_eval = min(min_eval, eval)
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth):
    best_move = None
    best_value = -float('inf') if board.turn == 0 else float('inf')
    
    alpha = -float('inf')
    beta = float('inf')
    
    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return None

    # Sorting for efficiency
    legal_moves.sort(key=lambda m: m.captured_piece is not None, reverse=True)
        
    for move in legal_moves:
        board.make_move(move)
        board_value = minimax(board, depth - 1, alpha, beta, board.turn != 0)
        board.unmake_move(move)
        
        if board.turn == 0: # White maximizing
            if board_value > best_value:
                best_value = board_value
                best_move = move
            alpha = max(alpha, best_value)
        else: # Black minimizing
            if board_value < best_value:
                best_value = board_value
                best_move = move
            beta = min(beta, best_value)
            
    return best_move

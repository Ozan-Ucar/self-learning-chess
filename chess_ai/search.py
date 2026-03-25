import time
from .evaluation import get_full_evaluation, PIECE_VALUES

def _move_order_score(move):
    # mvv lva
    
    score = 0
    if move.captured_piece is not None:
        score += PIECE_VALUES.get(move.captured_piece, 0) * 10
        score -= PIECE_VALUES.get(move.piece_type, 0)
    if move.promotion is not None:
        score += 800
    return score

# track nodes
nodes_searched = 0

def minimax(board, depth, alpha, beta, maximizing_player):
    global nodes_searched
    nodes_searched += 1
    
    if depth == 0:
        return get_full_evaluation(board)

    legal_moves = board.get_legal_moves()
    # captures first
    legal_moves.sort(key=_move_order_score, reverse=True)
    
    if not legal_moves:
        if board.is_in_check(board.turn):
            # Checkmate: negative infinity for the side in check
            return -100000 if maximizing_player else 100000
        return 0 # Stalemate
        
    if board.is_repetition():
        return 0 # Draw by threefold repetition

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

import random

def find_best_move(board, depth, epsilon=0.0):
    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return None, []

    # epsilon greedy for exploration
    if epsilon > 0.0 and random.random() < epsilon:
        return random.choice(legal_moves), []

    scored_moves = []
    best_moves = []
    best_value = -float('inf') if board.turn == 0 else float('inf')
    
    alpha = -float('inf')
    beta = float('inf')
    
    # sort captures first
    legal_moves.sort(key=_move_order_score, reverse=True)
        
    for move in legal_moves:
        board.make_move(move)
        board_value = minimax(board, depth - 1, alpha, beta, board.turn != 0)
        board.unmake_move(move)
        
        scored_moves.append((move, board_value))
        
        if board.turn == 0: # White maximizing
            if board_value > best_value:
                best_value = board_value
                best_moves = [move]
            elif board_value == best_value:
                best_moves.append(move)
            alpha = max(alpha, best_value)
        else: # Black minimizing
            if board_value < best_value:
                best_value = board_value
                best_moves = [move]
            elif board_value == best_value:
                best_moves.append(move)
            beta = min(beta, best_value)
    
    # sort best first
    is_white = board.turn == 0
    scored_moves.sort(key=lambda x: x[1], reverse=is_white)
    
    chosen = random.choice(best_moves) if best_moves else None
    return chosen, scored_moves

def find_best_move_timed(board, time_limit=2.0, max_depth=8, epsilon=0.0):
    # iterative deepening in time limit
    global nodes_searched
    nodes_searched = 0
    start = time.time()
    
    best_move = None
    best_depth = 0
    best_candidates = []
    
    for depth in range(1, max_depth + 1):
        elapsed = time.time() - start
        if elapsed >= time_limit:
            break
        
        move, candidates = find_best_move(board, depth, epsilon)
        if move is not None:
            best_move = move
            best_depth = depth
            best_candidates = candidates
        
        elapsed = time.time() - start
        if elapsed > time_limit * 0.5:
            break
    
    return best_move, best_depth, nodes_searched, best_candidates

from .constants import *

def get_pawn_moves(pawns, color, occupied, enemy_pieces, ep_sq=None):
    moves = 0
    ep_bb = (1 << ep_sq) if ep_sq is not None else 0
    
    if color == Color.WHITE:
        # Single push
        step1 = (pawns << 8) & ~occupied
        moves |= step1
        # Double push (only from rank 2)
        moves |= ((step1 & (RANK_3 | RANK_4)) << 8) & ~occupied # step1 must be true
        # Captures
        moves |= (pawns << 7) & (enemy_pieces | ep_bb) & ~FILE_H
        moves |= (pawns << 9) & (enemy_pieces | ep_bb) & ~FILE_A
    else:
        # Single push
        step1 = (pawns >> 8) & ~occupied
        moves |= step1
        # Double push (only from rank 7)
        moves |= ((step1 & (RANK_6 | RANK_5)) >> 8) & ~occupied # step1 must be true
        # Captures
        moves |= (pawns >> 7) & (enemy_pieces | ep_bb) & ~FILE_A
        moves |= (pawns >> 9) & (enemy_pieces | ep_bb) & ~FILE_H
    return moves

def get_knight_moves(knight_bitboard):
    moves = 0
    moves |= (knight_bitboard << 17) & ~FILE_A
    moves |= (knight_bitboard << 15) & ~FILE_H
    moves |= (knight_bitboard << 10) & ~(FILE_A | FILE_B)
    moves |= (knight_bitboard << 6) & ~(FILE_G | FILE_H)
    moves |= (knight_bitboard >> 17) & ~FILE_H
    moves |= (knight_bitboard >> 15) & ~FILE_A
    moves |= (knight_bitboard >> 10) & ~(FILE_G | FILE_H)
    moves |= (knight_bitboard >> 6) & ~(FILE_A | FILE_B)
    return moves

def get_sliding_moves(square_mask, occupied, color_occupied, directions):
    # Edge masks for each direction to prevent wrapping
    edge_masks = {
        N: RANK_8, S: RANK_1, E: FILE_H, W: FILE_A,
        NE: RANK_8 | FILE_H, NW: RANK_8 | FILE_A,
        SE: RANK_1 | FILE_H, SW: RANK_1 | FILE_A
    }
    
    moves = 0
    for d in directions:
        edge = edge_masks[d]
        curr = square_mask
        while True:
            if curr & edge: break

            if d > 0: curr <<= d
            else: curr >>= abs(d)

            if curr & color_occupied: break # Hit own piece
            moves |= curr
            if curr & occupied: break # Hit any piece (after adding capture)
    return moves

def get_king_moves(king_bitboard):
    moves = 0
    # The king moves one square in any direction
    moves |= (king_bitboard << 8) # N
    moves |= (king_bitboard >> 8) # S
    moves |= (king_bitboard << 1) & ~FILE_A # E
    moves |= (king_bitboard >> 1) & ~FILE_H # W
    moves |= (king_bitboard << 9) & ~FILE_A # NE
    moves |= (king_bitboard << 7) & ~FILE_H # NW
    moves |= (king_bitboard >> 7) & ~FILE_A # SE
    moves |= (king_bitboard >> 9) & ~FILE_H # SW
    return moves

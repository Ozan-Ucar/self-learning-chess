from .constants import *

def get_pawn_moves(pawns, color, occupied, enemy_pieces):
    moves = 0
    if color == Color.WHITE:
        # Single push
        moves |= (pawns << 8) & ~occupied
        # Double push (only from rank 2)
        moves |= ((pawns & RANK_2) << 16) & ~(occupied | (occupied << 8))
        # Captures
        moves |= (pawns << 7) & enemy_pieces & ~FILE_H
        moves |= (pawns << 9) & enemy_pieces & ~FILE_A
    else:
        # Single push
        moves |= (pawns >> 8) & ~occupied
        # Double push (only from rank 7)
        moves |= ((pawns & RANK_7) >> 16) & ~(occupied | (occupied >> 8))
        # Captures
        moves |= (pawns >> 7) & enemy_pieces & ~FILE_A
        moves |= (pawns >> 9) & enemy_pieces & ~FILE_H
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
    moves = 0
    for d in directions:
        curr = square_mask
        while True:
            # Check for board edges before shift
            if d == N and (curr & RANK_8): break
            if d == S and (curr & RANK_1): break
            if d == E and (curr & FILE_H): break
            if d == W and (curr & FILE_A): break
            if d == NE and (curr & (RANK_8 | FILE_H)): break
            if d == NW and (curr & (RANK_8 | FILE_A)): break
            if d == SE and (curr & (RANK_1 | FILE_H)): break
            if d == SW and (curr & (RANK_1 | FILE_A)): break

            if d > 0: curr <<= d
            else: curr >>= abs(d)

            if curr & color_occupied: break # Hit own piece
            moves |= curr
            if curr & occupied: break # Hit any piece (after adding capture)
    return moves

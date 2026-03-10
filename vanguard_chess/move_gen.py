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
    # Knights skip ranks and files
    moves = 0
    # North-North-East, etc. (The 8 L-shapes)
    moves |= (knight_bitboard << 17) & ~FILE_A
    moves |= (knight_bitboard << 15) & ~FILE_H
    moves |= (knight_bitboard << 10) & ~(FILE_A | FILE_B)
    moves |= (knight_bitboard << 6) & ~(FILE_G | FILE_H)
    moves |= (knight_bitboard >> 17) & ~FILE_H
    moves |= (knight_bitboard >> 15) & ~FILE_A
    moves |= (knight_bitboard >> 10) & ~(FILE_G | FILE_H)
    moves |= (knight_bitboard >> 6) & ~(FILE_A | FILE_B)
    return moves

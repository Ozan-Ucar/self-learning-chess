from enum import IntEnum

class Color(IntEnum):
    WHITE = 0
    BLACK = 1

class Piece(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

# Directions for bitboard shifts
N = 8
S = -8
E = 1
W = -1
NE = 9
NW = 7
SE = -7
SW = -9

# Rank and File masks
FILE_A = 0x0101010101010101
FILE_B = FILE_A << 1
FILE_C = FILE_A << 2
FILE_D = FILE_A << 3
FILE_E = FILE_A << 4
FILE_F = FILE_A << 5
FILE_G = FILE_A << 6
FILE_H = FILE_A << 7

RANK_1 = 0x00000000000000FF
RANK_2 = RANK_1 << 8
RANK_3 = RANK_1 << 16
RANK_4 = RANK_1 << 24
RANK_5 = RANK_1 << 32
RANK_6 = RANK_1 << 40
RANK_7 = RANK_1 << 48
RANK_8 = RANK_1 << 56

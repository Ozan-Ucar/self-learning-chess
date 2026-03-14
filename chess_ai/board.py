from .constants import *

class Board:
    def __init__(self):
        # Bitboards for each piece type and color
        self.pieces = {
            Color.WHITE: [0] * 6,
            Color.BLACK: [0] * 6
        }
        self.turn = Color.WHITE
        self.reset_board()

    def reset_board(self):
        # The standard starting position FEN
        self.set_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        
    def set_from_fen(self, fen):
        # Clear board
        for c in [Color.WHITE, Color.BLACK]:
            for p in Piece:
                self.pieces[c][p] = 0
                
        parts = fen.split()
        if not parts: return
        board_str = parts[0]
        
        row, col = 7, 0
        for char in board_str:
            if char == '/':
                row -= 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                color = Color.WHITE if char.isupper() else Color.BLACK
                c_idx = 'PNBRQK'.index(char.upper())
                pt = Piece(c_idx)
                
                self.pieces[color][pt] |= (1 << (row * 8 + col))
                col += 1
                
        if len(parts) > 1:
            self.turn = Color.WHITE if parts[1] == 'w' else Color.BLACK

    def get_occupancy(self, color=None):
        if color is not None:
            return sum(self.pieces[color])
        return sum(self.pieces[Color.WHITE]) | sum(self.pieces[Color.BLACK])

    def print_board(self):
        piece_chars = {
            Piece.PAWN: 'P', Piece.KNIGHT: 'N', Piece.BISHOP: 'B',
            Piece.ROOK: 'R', Piece.QUEEN: 'Q', Piece.KING: 'K'
        }
        
        for r in range(7, -1, -1):
            row_str = f"{r+1} "
            for f in range(8):
                idx = r * 8 + f
                mask = 1 << idx
                
                char = ". "
                for color in [Color.WHITE, Color.BLACK]:
                    for pt in Piece:
                        if self.pieces[color][pt] & mask:
                            c = piece_chars[pt]
                            char = (c if color == Color.WHITE else c.lower()) + " "
                            break
                row_str += char
            print(row_str)
        print("  a b c d e f g h")

    def make_move(self, move):
        # Simplistic move execution for search (no castling/en passant yet)
        color = self.turn
        opponent = 1 - color
        
        # Remove moving piece from its current square
        self.pieces[color][move.piece_type] &= ~(1 << move.from_sq)
        
        # Handle captures
        if move.captured_piece is not None:
             self.pieces[opponent][move.captured_piece] &= ~(1 << move.to_sq)
             
        # Add piece to destination square
        if move.promotion is not None:
            self.pieces[color][move.promotion] |= (1 << move.to_sq)
        else:
            self.pieces[color][move.piece_type] |= (1 << move.to_sq)
            
        self.turn = opponent

    def unmake_move(self, move):
        # Reverse the move logic
        self.turn = 1 - self.turn
        color = self.turn
        opponent = 1 - color
        
        target_piece = move.promotion if move.promotion is not None else move.piece_type
        self.pieces[color][target_piece] &= ~(1 << move.to_sq)
        self.pieces[color][move.piece_type] |= (1 << move.from_sq)
        
        if move.captured_piece is not None:
            self.pieces[opponent][move.captured_piece] |= (1 << move.to_sq)

    def get_fen(self):
        # A simple FEN generator for debugging with external tools
        fen = ""
        for r in range(7, -1, -1):
            empty = 0
            for f in range(8):
                mask = 1 << (r * 8 + f)
                found = False
                for color in [Color.WHITE, Color.BLACK]:
                    for pt in Piece:
                        if self.pieces[color][pt] & mask:
                            if empty > 0:
                                fen += str(empty)
                                empty = 0
                            char = "PNBRQK"[pt]
                            fen += char if color == Color.WHITE else char.lower()
                            found = True
                            break
                if not found:
                    empty += 1
            if empty > 0:
                fen += str(empty)
            if r > 0:
                fen += "/"
        
        turn = "w" if self.turn == Color.WHITE else "b"
        return f"{fen} {turn} - - 0 1"

    def is_attacked(self, square, by_color):
        # Checks if a square is attacked by any piece of the given color
        square_mask = 1 << square
        occupied = self.get_occupancy()
        enemy_pieces = self.pieces[by_color]
        
        from .move_gen import get_pawn_moves, get_knight_moves, get_king_moves, get_sliding_moves
        
        # Check Knights
        if get_knight_moves(square_mask) & enemy_pieces[Piece.KNIGHT]: return True
        
        # Check King
        if get_king_moves(square_mask) & enemy_pieces[Piece.KING]: return True
        
        # Check Pawns (reverse direction as it's an attack TO the square)
        if by_color == Color.WHITE:
             attacks = (square_mask >> 7) & ~FILE_A | (square_mask >> 9) & ~FILE_H
        else:
             attacks = (square_mask << 7) & ~FILE_H | (square_mask << 9) & ~FILE_A
        if attacks & enemy_pieces[Piece.PAWN]: return True
        
        # Check Sliders (Bishop, Rook, Queen)
        if get_sliding_moves(square_mask, occupied, 0, (NE, NW, SE, SW)) & \
           (enemy_pieces[Piece.BISHOP] | enemy_pieces[Piece.QUEEN]): return True
        if get_sliding_moves(square_mask, occupied, 0, (N, S, E, W)) & \
           (enemy_pieces[Piece.ROOK] | enemy_pieces[Piece.QUEEN]): return True
           
        return False

    def is_in_check(self, color):
        king_bb = self.pieces[color][Piece.KING]
        if not king_bb: return False 
        king_square = king_bb.bit_length() - 1
        return self.is_attacked(king_square, 1 - color)

    def get_legal_moves(self):
        # We'll need a better piece-to-moves map, but this works for now
        from .move import Move
        from .move_gen import get_pawn_moves, get_knight_moves, get_king_moves, get_sliding_moves
        
        color = self.turn
        occupied = self.get_occupancy()
        own_pieces = self.get_occupancy(color)
        enemy_pieces_occ = self.get_occupancy(1 - color)
        
        legal_moves = []
        
        # Iterate over all pieces of current color
        for piece_type in Piece:
            pieces = self.pieces[color][piece_type]
            for i in range(64):
                if not (pieces & (1 << i)): continue
                
                # Get pseudo-legal moves for this piece
                pseudo_moves = 0
                if piece_type == Piece.PAWN:
                    pseudo_moves = get_pawn_moves(1 << i, color, occupied, enemy_pieces_occ)
                elif piece_type == Piece.KNIGHT:
                    pseudo_moves = get_knight_moves(1 << i) & ~own_pieces
                elif piece_type == Piece.KING:
                    pseudo_moves = get_king_moves(1 << i) & ~own_pieces
                elif piece_type == Piece.BISHOP:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (NE, NW, SE, SW))
                elif piece_type == Piece.ROOK:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (N, S, E, W))
                elif piece_type == Piece.QUEEN:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (N, S, E, W, NE, NW, SE, SW))
                
                # Validate moves (must not leave king in check)
                for j in range(64):
                    if not (pseudo_moves & (1 << j)): continue
                    
                    # Create move object
                    captured = None
                    for pt in Piece:
                        if self.pieces[1-color][pt] & (1 << j):
                            captured = pt; break
                    
                    move = Move(i, j, piece_type, captured_piece=captured)
                    
                    # Try it
                    self.make_move(move)
                    if not self.is_in_check(color):
                        legal_moves.append(move)
                    self.unmake_move(move)
                    
        return legal_moves

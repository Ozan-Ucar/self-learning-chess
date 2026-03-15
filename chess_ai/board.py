from .constants import *

class Board:
    def __init__(self):
        # Bitboards for each piece type and color
        self.pieces = {
            Color.WHITE: [0] * 6,
            Color.BLACK: [0] * 6
        }
        self.turn = Color.WHITE
        self.en_passant_sq = None
        self.history = []
        
        # Castling rights: K, Q, k, q
        self.castling_rights = {
            'K': True, 'Q': True,
            'k': True, 'q': True
        }
        
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
            
        # Parse castling rights from FEN
        # Reset all first
        self.castling_rights = { 'K': False, 'Q': False, 'k': False, 'q': False }
        if len(parts) > 2 and parts[2] != '-':
            for right in parts[2]:
                if right in self.castling_rights:
                    self.castling_rights[right] = True
                    
        self.en_passant_sq = None
        if len(parts) > 3 and parts[3] != '-':
            f = 'abcdefgh'.index(parts[3][0])
            r = int(parts[3][1]) - 1
            self.en_passant_sq = r * 8 + f
            
        self.history = []
        self.state_history = []

    def get_hash(self):
        return hash(tuple(self.pieces[Color.WHITE] + self.pieces[Color.BLACK] + [self.turn, self.en_passant_sq] + list(self.castling_rights.values())))
        
    def is_repetition(self):
        if not hasattr(self, 'history'): return False
        # If the current state has already appeared 2 times in history, 
        # this makes it the 3rd time (Threefold Repetition)
        return self.history.count(self.get_hash()) >= 2


    def get_occupancy(self, color=None):
        if color is not None:
            return sum(self.pieces[color])
        return sum(self.pieces[Color.WHITE]) | sum(self.pieces[Color.BLACK])

    def print_board(self, pretty=False):
        import sys
        import os
        
        is_windows = os.name == 'nt'
        if is_windows:
            os.system("") # Enable ANSI escape sequences in Windows terminal
            
        if pretty and hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
            
        piece_chars = {
            Piece.PAWN: 'P', Piece.KNIGHT: 'N', Piece.BISHOP: 'B',
            Piece.ROOK: 'R', Piece.QUEEN: 'Q', Piece.KING: 'K'
        }
        
        # Hollow pieces (look cleaner on dark terminals, avoid emoji substitution on Windows)
        hollow = {Piece.PAWN: '♙', Piece.KNIGHT: '♘', Piece.BISHOP: '♗', Piece.ROOK: '♖', Piece.QUEEN: '♕', Piece.KING: '♔'}
        # Solid pieces (Windows renders these as purple emojis incorrectly)
        solid  = {Piece.PAWN: '♟', Piece.KNIGHT: '♞', Piece.BISHOP: '♝', Piece.ROOK: '♜', Piece.QUEEN: '♛', Piece.KING: '♚'}
        
        for r in range(7, -1, -1):
            row_str = f"{r+1} "
            for f in range(8):
                idx = r * 8 + f
                mask = 1 << idx
                
                char = ". "
                for color in [Color.WHITE, Color.BLACK]:
                    for pt in Piece:
                        if self.pieces[color][pt] & mask:
                            if pretty:
                                if is_windows:
                                    # Fallback for Windows: Use hollow pieces for both, color Black blue/cyan
                                    if color == Color.WHITE:
                                        char = hollow[pt] + " "
                                    else:
                                        char = f"\033[36m{hollow[pt]}\033[0m " # 36m is Cyan
                                else:
                                    char = (hollow[pt] if color == Color.WHITE else solid[pt]) + " "
                            else:
                                c = piece_chars[pt]
                                char = (c if color == Color.WHITE else c.lower()) + " "
                            break
                row_str += char
            print(row_str)
        print("  a b c d e f g h")


    def make_move(self, move):
        if not hasattr(self, 'history'): self.history = []
        if not hasattr(self, 'state_history'): self.state_history = []
        
        self.history.append(self.get_hash())
        self.state_history.append((self.en_passant_sq, dict(self.castling_rights)))
        
        color = self.turn
        opponent = 1 - color
        
        # Remove moving piece from its current square
        self.pieces[color][move.piece_type] &= ~(1 << move.from_sq)
        
        # Handle captures
        if move.captured_piece is not None:
             if move.is_en_passant:
                 ep_capture_sq = (move.from_sq // 8) * 8 + (move.to_sq % 8)
                 self.pieces[opponent][move.captured_piece] &= ~(1 << ep_capture_sq)
             else:
                 self.pieces[opponent][move.captured_piece] &= ~(1 << move.to_sq)
             
        # Add piece to destination square
        if move.promotion is not None:
            self.pieces[color][move.promotion] |= (1 << move.to_sq)
        else:
            self.pieces[color][move.piece_type] |= (1 << move.to_sq)
            
        # Handle Castling (move the rook)
        if move.is_castling:
            if move.to_sq == 6:   # White Kingside
                self.pieces[color][Piece.ROOK] &= ~(1 << 7)
                self.pieces[color][Piece.ROOK] |= (1 << 5)
            elif move.to_sq == 2: # White Queenside
                self.pieces[color][Piece.ROOK] &= ~(1 << 0)
                self.pieces[color][Piece.ROOK] |= (1 << 3)
            elif move.to_sq == 62: # Black Kingside
                self.pieces[color][Piece.ROOK] &= ~(1 << 63)
                self.pieces[color][Piece.ROOK] |= (1 << 61)
            elif move.to_sq == 58: # Black Queenside
                self.pieces[color][Piece.ROOK] &= ~(1 << 56)
                self.pieces[color][Piece.ROOK] |= (1 << 59)
                
        # Update En Passant Target
        self.en_passant_sq = None
        if move.piece_type == Piece.PAWN and abs(move.from_sq - move.to_sq) == 16:
            self.en_passant_sq = (move.from_sq + move.to_sq) // 2
            
        # Revoke castling rights if King or Rooks move
        if move.piece_type == Piece.KING:
            if color == Color.WHITE:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        elif move.piece_type == Piece.ROOK:
            if move.from_sq == 0: self.castling_rights['Q'] = False   # a1
            elif move.from_sq == 7: self.castling_rights['K'] = False # h1
            elif move.from_sq == 56: self.castling_rights['q'] = False # a8
            elif move.from_sq == 63: self.castling_rights['k'] = False # h8
            
        # Also revoke if a rook on corners gets captured
        if move.to_sq == 0: self.castling_rights['Q'] = False
        elif move.to_sq == 7: self.castling_rights['K'] = False
        elif move.to_sq == 56: self.castling_rights['q'] = False
        elif move.to_sq == 63: self.castling_rights['k'] = False
            
        self.turn = opponent

    def unmake_move(self, move):
        if hasattr(self, 'history') and self.history:
            self.history.pop()
        self.en_passant_sq, self.castling_rights = self.state_history.pop()
            
        # Reverse the move logic
        self.turn = 1 - self.turn
        color = self.turn
        opponent = 1 - color
        
        target_piece = move.promotion if move.promotion is not None else move.piece_type
        self.pieces[color][target_piece] &= ~(1 << move.to_sq)
        self.pieces[color][move.piece_type] |= (1 << move.from_sq)
        
        if move.captured_piece is not None:
            if move.is_en_passant:
                 ep_capture_sq = (move.from_sq // 8) * 8 + (move.to_sq % 8)
                 self.pieces[opponent][move.captured_piece] |= (1 << ep_capture_sq)
            else:
                 self.pieces[opponent][move.captured_piece] |= (1 << move.to_sq)
                 
        if move.is_castling:
            if move.to_sq == 6:   # White Kingside
                self.pieces[color][Piece.ROOK] &= ~(1 << 5)
                self.pieces[color][Piece.ROOK] |= (1 << 7)
            elif move.to_sq == 2: # White Queenside
                self.pieces[color][Piece.ROOK] &= ~(1 << 3)
                self.pieces[color][Piece.ROOK] |= (1 << 0)
            elif move.to_sq == 62: # Black Kingside
                self.pieces[color][Piece.ROOK] &= ~(1 << 61)
                self.pieces[color][Piece.ROOK] |= (1 << 63)
            elif move.to_sq == 58: # Black Queenside
                self.pieces[color][Piece.ROOK] &= ~(1 << 59)
                self.pieces[color][Piece.ROOK] |= (1 << 56)

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
                    pseudo_moves = get_pawn_moves(1 << i, color, occupied, enemy_pieces_occ, self.en_passant_sq)
                elif piece_type == Piece.KNIGHT:
                    pseudo_moves = get_knight_moves(1 << i) & ~own_pieces
                elif piece_type == Piece.KING:
                    pseudo_moves = get_king_moves(1 << i) & ~own_pieces
                    # Castling moves
                    if color == Color.WHITE and i == 4 and not self.is_attacked(4, Color.BLACK):
                        if self.castling_rights['K'] and not (occupied & 0x60) and not self.is_attacked(5, Color.BLACK):
                            pseudo_moves |= (1 << 6) # g1
                        if self.castling_rights['Q'] and not (occupied & 0xE) and not self.is_attacked(3, Color.BLACK):
                            pseudo_moves |= (1 << 2) # c1
                    elif color == Color.BLACK and i == 60 and not self.is_attacked(60, Color.WHITE):
                        if self.castling_rights['k'] and not (occupied & 0x6000000000000000) and not self.is_attacked(61, Color.WHITE):
                            pseudo_moves |= (1 << 62) # g8
                        if self.castling_rights['q'] and not (occupied & 0x0E00000000000000) and not self.is_attacked(59, Color.WHITE):
                            pseudo_moves |= (1 << 58) # c8
                elif piece_type == Piece.BISHOP:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (NE, NW, SE, SW))
                elif piece_type == Piece.ROOK:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (N, S, E, W))
                elif piece_type == Piece.QUEEN:
                    pseudo_moves = get_sliding_moves(1 << i, occupied, own_pieces, (N, S, E, W, NE, NW, SE, SW))
                
                # Validate moves (must not leave king in check)
                for j in range(64):
                    if not (pseudo_moves & (1 << j)): continue
                    
                    captured = None
                    for pt in Piece:
                        if self.pieces[1-color][pt] & (1 << j):
                            captured = pt; break
                            
                    is_ep = False
                    if piece_type == Piece.PAWN and j == self.en_passant_sq:
                        captured = Piece.PAWN
                        is_ep = True
                        
                    is_castling = False
                    if piece_type == Piece.KING and abs(i - j) == 2:
                        is_castling = True

                    moves_to_try = []
                    if piece_type == Piece.PAWN and (j // 8 == 0 or j // 8 == 7): # Promotion
                        for p in [Piece.QUEEN, Piece.ROOK, Piece.BISHOP, Piece.KNIGHT]:
                            moves_to_try.append(Move(i, j, piece_type, captured_piece=captured, promotion=p))
                    else:
                        moves_to_try.append(Move(i, j, piece_type, captured_piece=captured, is_castling=is_castling, is_en_passant=is_ep))
                    
                    for move in moves_to_try:
                        self.make_move(move)
                        if not self.is_in_check(color):
                            legal_moves.append(move)
                        self.unmake_move(move)
                        
        return legal_moves

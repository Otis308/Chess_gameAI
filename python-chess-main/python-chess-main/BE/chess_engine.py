# backend/chess_engine.py

import chess # type: ignore
import random

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()
        self.depth_map = {
            "Nhập Môn": 1,
            "Thành Thạo": 2,
            "Cao Thủ": 3,
            "Kiện Tướng": 4 
        }

    def reset_board(self):
        self.board.reset()

    def make_move(self, uci_move):
        """Thực hiện nước đi nếu hợp lệ."""
        move = chess.Move.from_uci(uci_move)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def is_game_over(self):
        """Kiểm tra trạng thái kết thúc game."""
        return self.board.is_game_over()

    def get_status(self):
        """Trả về trạng thái hiện tại."""
        status = {
            'fen': self.board.fen(),
            'turn': 'white' if self.board.turn == chess.WHITE else 'black',
            'game_over': self.board.is_game_over(),
            'outcome': self.board.outcome().result() if self.board.is_game_over() else None,
            'captured_white': self._get_captured_pieces(chess.WHITE),
            'captured_black': self._get_captured_pieces(chess.BLACK),
            'legal_moves': [move.uci() for move in self.board.legal_moves]
        }
        return status
    
    def _get_captured_pieces(self, color):
        # Lấy danh sách quân cờ đã bị bắt (Đây là một cách đơn giản, cần logic phức tạp hơn cho hiển thị chính xác)
        # Trong python-chess, bạn cần theo dõi thủ công hoặc tính toán từ FEN
        # Để đơn giản, ta chỉ trả về placeholder
        return ['P', 'N'] if color == chess.WHITE else ['p', 'n'] 

    def undo_move(self):
        """Quay lại nước đi."""
        if self.board.move_stack:
            self.board.pop()
            return True
        return False

    def get_ai_move(self, level):
        """Tính toán nước đi của AI bằng Minimax."""
        depth = self.depth_map.get(level, 3)
        
        # Đảm bảo độ sâu không quá lớn nếu không sẽ rất chậm
        if depth > 4: depth = 4
        
        best_move = self._minimax_root(depth, self.board)
        return best_move.uci() if best_move else None

    # --- Thuật toán Minimax với Cắt tỉa Alpha-Beta ---

    def _evaluate_board(self, board):
        # Đánh giá đơn giản: giá trị quân cờ
        value_map = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 200 # King có giá trị cao nhất
        }
        score = 0
        for piece_type, value in value_map.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
        
        return score

    def _minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self._evaluate_board(board)

        if maximizing_player:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval

    def _minimax_root(self, depth, board):
        is_white_turn = board.turn == chess.WHITE
        best_move = None
        
        # Nếu là lượt Trắng, tìm kiếm điểm số cao nhất (Max); nếu là Đen, tìm kiếm điểm số thấp nhất (Min)
        best_score = -float('inf') if is_white_turn else float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            
            # Đánh giá nước đi. Cấp độ tìm kiếm ngược lại với người chơi hiện tại
            score = self._minimax(board, depth - 1, -float('inf'), float('inf'), not is_white_turn)
            board.pop()
            
            if is_white_turn:
                if score > best_score:
                    best_score = score
                    best_move = move
            else: # Lượt Đen
                if score < best_score:
                    best_score = score
                    best_move = move
                    
        return best_move

# --- Gợi ý nước đi (cho tính năng Gợi ý) ---
    def get_hint_move(self, depth=2):
        """Cung cấp nước đi tốt nhất với độ sâu nông."""
        return self._minimax_root(depth, self.board).uci()
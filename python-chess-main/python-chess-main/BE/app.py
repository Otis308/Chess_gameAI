# backend/app.py

from flask import Flask, render_template, request, jsonify # type: ignore
from flask_sock import Sock # type: ignore
from chess_engine import ChessEngine
import json
import random
import string
import uuid

app = Flask(__name__, 
            static_folder='../frontend', 
            template_folder='../frontend')
sock = Sock(app)

# --- Quản lý trạng thái Game ---
# Sử dụng dictionary để lưu trữ nhiều phiên game (AI, Local, Online)
games = {} # {game_id: ChessEngine object}
rooms = {} # {room_code: game_id}
waiting_player_ws = None # WebSocket của người chơi đang chờ ghép ngẫu nhiên

# --- Quản lý WebSocket Sessions ---
ws_sessions = {} # {session_id: ws}

def generate_room_code():
    """Tạo mã phòng ngẫu nhiên 6 chữ số (1-9)."""
    return ''.join(random.choices(string.digits.replace('0', ''), k=6))

@app.route('/')
def index():
    """Phục vụ trang HTML chính."""
    return render_template('index.html')

# --- API cho Game AI ---

@app.route('/api/start_ai', methods=['POST'])
def start_ai_game():
    data = request.json
    level = data.get('level', 'Thành Thạo')
    game_id = str(uuid.uuid4())
    
    engine = ChessEngine()
    games[game_id] = {'engine': engine, 'level': level, 'mode': 'AI'}
    
    return jsonify({
        'game_id': game_id,
        'status': engine.get_status()
    })

@app.route('/api/ai_move/<game_id>', methods=['POST'])
def ai_move(game_id):
    game_data = games.get(game_id)
    if not game_data or game_data['mode'] != 'AI':
        return jsonify({'error': 'Game not found or not AI mode'}), 404
    
    engine = game_data['engine']
    
    # Lấy nước đi của người chơi
    player_uci = request.json.get('uci')
    engine.make_move(player_uci)
    
    # Kiểm tra kết thúc game sau nước đi người chơi
    if engine.is_game_over():
        return jsonify(engine.get_status())
    
    # Lấy nước đi của AI
    ai_uci = engine.get_ai_move(game_data['level'])
    if ai_uci:
        engine.make_move(ai_uci)
        
    return jsonify(engine.get_status())

@app.route('/api/ai_controls/<game_id>', methods=['POST'])
def ai_controls(game_id):
    game_data = games.get(game_id)
    if not game_data:
        return jsonify({'error': 'Game not found'}), 404
        
    engine = game_data['engine']
    action = request.json.get('action')
    
    if action == 'undo':
        engine.undo_move()
        # Quay lại 2 lần (nước đi của AI và người chơi)
        if engine.undo_move(): 
            return jsonify(engine.get_status())
        else:
            return jsonify({'status': 'Board is empty'})
            
    elif action == 'hint':
        hint = engine.get_hint_move()
        return jsonify({'hint': hint})
        
    elif action == 'restart':
        engine.reset_board()
        return jsonify(engine.get_status())

    return jsonify({'error': 'Invalid action'}), 400

# --- WebSocket cho Multiplayer (Ngẫu nhiên/Tạo phòng) ---

@sock.route('/ws/multiplayer')
def multiplayer_ws(ws):
    global waiting_player_ws
    
    session_id = str(uuid.uuid4())
    ws_sessions[session_id] = ws
    print(f"New connection: {session_id}")

    try:
        while True:
            data = ws.receive()
            if data is None: break
            message = json.loads(data)
            
            action = message.get('action')
            game_id = message.get('game_id')
            
            # --- 1. Tạo phòng ---
            if action == 'create_room':
                room_code = generate_room_code()
                game_id = str(uuid.uuid4())
                engine = ChessEngine()
                
                games[game_id] = {'engine': engine, 'players': {session_id: 'white'}, 'mode': 'Multiplayer'}
                rooms[room_code] = game_id
                
                ws.send(json.dumps({
                    'status': 'room_created', 
                    'room_code': room_code, 
                    'player_color': 'white',
                    'game_id': game_id,
                    'game_status': engine.get_status()
                }))
                
            # --- 2. Tham gia phòng ---
            elif action == 'join_room':
                room_code = message.get('room_code')
                game_id = rooms.get(room_code)
                
                if game_id and len(games[game_id]['players']) < 2:
                    games[game_id]['players'][session_id] = 'black'
                    
                    # Thông báo cho người chơi 1 (Trắng)
                    player1_session_id = list(games[game_id]['players'].keys())[0]
                    ws_sessions[player1_session_id].send(json.dumps({'status': 'player_joined'}))
                    
                    # Thông báo cho người chơi 2 (Đen)
                    ws.send(json.dumps({
                        'status': 'room_joined', 
                        'player_color': 'black',
                        'game_id': game_id,
                        'game_status': games[game_id]['engine'].get_status()
                    }))
                else:
                    ws.send(json.dumps({'status': 'error', 'message': 'Room not found or full'}))

            # --- 3. Ghép ngẫu nhiên ---
            elif action == 'match_random':
                if waiting_player_ws and waiting_player_ws != ws:
                    # Ghép đôi
                    player1_session_id = [sid for sid, w in ws_sessions.items() if w == waiting_player_ws][0]
                    player2_session_id = session_id
                    
                    game_id = str(uuid.uuid4())
                    engine = ChessEngine()
                    games[game_id] = {'engine': engine, 'players': {player1_session_id: 'white', player2_session_id: 'black'}, 'mode': 'Multiplayer'}
                    
                    # Báo cho P1 (Trắng)
                    waiting_player_ws.send(json.dumps({
                        'status': 'matched', 
                        'player_color': 'white',
                        'game_id': game_id,
                        'game_status': engine.get_status()
                    }))
                    
                    # Báo cho P2 (Đen)
                    ws.send(json.dumps({
                        'status': 'matched', 
                        'player_color': 'black',
                        'game_id': game_id,
                        'game_status': engine.get_status()
                    }))
                    waiting_player_ws = None # Reset người chờ
                else:
                    waiting_player_ws = ws
                    ws.send(json.dumps({'status': 'waiting', 'message': 'Waiting for another player...'}))

            # --- 4. Thực hiện nước đi (Áp dụng chung) ---
            elif action == 'move':
                uci_move = message.get('uci')
                game_data = games.get(game_id)
                
                if game_data and game_data['mode'] == 'Multiplayer':
                    engine = game_data['engine']
                    player_color = game_data['players'][session_id]
                    
                    # Kiểm tra lượt đi
                    if engine.board.turn == (chess.WHITE if player_color == 'white' else chess.BLACK): # type: ignore
                        if engine.make_move(uci_move):
                            # Gửi trạng thái game mới đến tất cả người chơi trong phòng
                            new_status = engine.get_status()
                            for sid, color in game_data['players'].items():
                                if sid in ws_sessions:
                                    ws_sessions[sid].send(json.dumps({'status': 'update', 'game_status': new_status}))
                            
    except Exception as e:
        print(f"WebSocket Error for {session_id}: {e}")
    finally:
        # Xử lý khi người chơi ngắt kết nối
        print(f"Connection closed: {session_id}")
        del ws_sessions[session_id]
        # Xử lý dọn dẹp game, phòng chờ, v.v.

if __name__ == '__main__':
    # Chạy trên cổng 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
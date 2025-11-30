// ================= CONFIG =================
const PIECE_MAP = {
  'p':'♟','n':'♞','b':'♝','r':'♜','q':'♛','k':'♚',
  'P':'♙','N':'♘','B':'♗','R':'♖','Q':'♕','K':'♔'
};

// ================= AI CONFIG =================
const AI_LEVELS = {
  1: { name: "Nhập môn", depth: 2, randomness: 0.3 },
  2: { name: "Thành thạo", depth: 3, randomness: 0.15 },
  3: { name: "Cao thủ", depth: 4, randomness: 0.05 },
  4: { name: "Kiện tướng", depth: 5, randomness: 0 }
};

const PIECE_VALUES = {
  'p': 10, 'n': 30, 'b': 30, 'r': 50, 'q': 90, 'k': 900,
  'P': -10, 'N': -30, 'B': -30, 'R': -50, 'Q': -90, 'K': -900
};

const PAWN_TABLE = [
  [0,  0,  0,  0,  0,  0,  0,  0],
  [50, 50, 50, 50, 50, 50, 50, 50],
  [10, 10, 20, 30, 30, 20, 10, 10],
  [5,  5, 10, 25, 25, 10,  5,  5],
  [0,  0,  0, 20, 20,  0,  0,  0],
  [5, -5,-10,  0,  0,-10, -5,  5],
  [5, 10, 10,-20,-20, 10, 10,  5],
  [0,  0,  0,  0,  0,  0,  0,  0]
];

const KNIGHT_TABLE = [
  [-50,-40,-30,-30,-30,-30,-40,-50],
  [-40,-20,  0,  0,  0,  0,-20,-40],
  [-30,  0, 10, 15, 15, 10,  0,-30],
  [-30,  5, 15, 20, 20, 15,  5,-30],
  [-30,  0, 15, 20, 20, 15,  0,-30],
  [-30,  5, 10, 15, 15, 10,  5,-30],
  [-40,-20,  0,  5,  5,  0,-20,-40],
  [-50,-40,-30,-30,-30,-30,-40,-50]
];

// ================= STATE =================
let board = [];
let selected = null;
let legalMoves = [];
let capturedWhite = [];
let capturedBlack = [];
let turn = "white";
let boardOrientation = "white"; 
let playerColor = null;
let aiColor = null;
let aiLevel = 2;
let isAIThinking = false;
let timer = 300;
let timerInterval = null;
let moveHistory = [];
let hintEnabled = true;

// ================= DOM =================
const chessboard = document.getElementById("chessboard");
const chooseColorModal = document.getElementById("chooseColorModal");
const btnWhite = document.getElementById("chooseWhite");
const btnBlack = document.getElementById("chooseBlack");

const btnRestart = document.getElementById("btn-restart");
const btnUndo = document.getElementById("btn-undo");
const btnRules = document.getElementById("btn-rules");
const rulesModal = document.getElementById("rules-modal");

const btnTimeUp = document.getElementById("btn-time-up");
const btnTimeDown = document.getElementById("btn-time-down");
const btnTimeStart = document.getElementById("btn-time-start");
const btnTimePause = document.getElementById("btn-time-pause");
const btnTimeReset = document.getElementById("btn-time-reset");
const timerDisplay = document.getElementById("timer-display");

const timeupModal = document.getElementById("timeup-modal");
const closeTimeupModal = document.getElementById("closeTimeupModal");

const toggleHint = document.getElementById("toggle-hint");
const aiEngine = {
    getBestMove: function(level) {
        return { from: "e2", to: "e4" };
    }
};

// ================= AI FUNCTIONS =================

function evaluateBoard(board) {
  let score = 0;
  
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const piece = board[r][c];
      if (!piece) continue;
      
      const isWhite = piece === piece.toUpperCase();
      let pieceValue = PIECE_VALUES[piece];
      
      if (piece.toLowerCase() === 'p') {
        const posValue = isWhite ? PAWN_TABLE[7-r][c] : PAWN_TABLE[r][c];
        pieceValue += isWhite ? -posValue/10 : posValue/10;
      } else if (piece.toLowerCase() === 'n') {
        const posValue = isWhite ? KNIGHT_TABLE[7-r][c] : KNIGHT_TABLE[r][c];
        pieceValue += isWhite ? -posValue/10 : posValue/10;
      }
      
      score += pieceValue;
    }
  }
  
  return score;
}

function getAllMovesForAI(board, color) {
  const moves = [];
  
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const piece = board[r][c];
      if (!piece) continue;
      
      const isWhite = piece === piece.toUpperCase();
      if ((color === "white" && !isWhite) || (color === "black" && isWhite)) {
        continue;
      }
      
      const pieceMoves = getMovesForAI(board, r, c);
      for (const [tr, tc] of pieceMoves) {
        moves.push({ from: [r, c], to: [tr, tc], piece });
      }
    }
  }
  
  return moves;
}

function updateBoard(move) {
    // 1. Lấy quân cờ ở ô xuất phát
    const piece = board.getPieceAt(move.from);

    // 2. Xóa quân khỏi ô xuất phát
    board.removePieceAt(move.from);

    // 3. Đặt quân vào ô đích
    board.setPieceAt(move.to, piece);

    // 4. Vẽ lại bàn cờ
    renderBoard(board);

    console.log("AI đã đi quân:", piece, "từ", move.from, "đến", move.to);
}

function minimax(board, depth, alpha, beta, isMaximizing, aiColor) {
  if (depth === 0) {
    return evaluateBoard(board);
  }
  
  const currentColor = isMaximizing ? 
    (aiColor === "black" ? "black" : "white") : 
    (aiColor === "black" ? "white" : "black");
  
  const moves = getAllMovesForAI(board, currentColor);
  
  if (moves.length === 0) {
    return isMaximizing ? -10000 : 10000;
  }
  
  if (isMaximizing) {
    let maxEval = -Infinity;
    
    for (const move of moves) {
      const newBoard = makeMoveAI(board, move.from, move.to);
      const evaluation = minimax(newBoard, depth - 1, alpha, beta, false, aiColor);
      maxEval = Math.max(maxEval, evaluation);
      alpha = Math.max(alpha, evaluation);
      
      if (beta <= alpha) break; // Alpha-Beta Pruning
    }
    
    return maxEval;
  } else {
    let minEval = Infinity;
    
    for (const move of moves) {
      const newBoard = makeMoveAI(board, move.from, move.to);
      const evaluation = minimax(newBoard, depth - 1, alpha, beta, true, aiColor);
      minEval = Math.min(minEval, evaluation);
      beta = Math.min(beta, evaluation);
      
      if (beta <= alpha) break; // Alpha-Beta Pruning
    }
    
    return minEval;
  }
}

function makeMoveAI(board, from, to) {
  // Clone sâu bàn cờ (giả sử board là mảng 2D các ô, ô trống là "")
  const newBoard = board.map(row => row.slice());

  const [fr, fc] = from;
  const [tr, tc] = to;

  // Di chuyển quân trên bản sao
  newBoard[tr][tc] = newBoard[fr][fc];
  newBoard[fr][fc] = "";

  return newBoard;
}

function drawCapturedPieces() {
  const whiteCapturedEl = document.getElementById("captured-white");
  const blackCapturedEl = document.getElementById("captured-black");

  if (whiteCapturedEl) {
    whiteCapturedEl.innerHTML = capturedWhite.join(" ");
  }
  if (blackCapturedEl) {
    blackCapturedEl.innerHTML = capturedBlack.join(" ");
  }
}

function makeAIMove() {
  if (isAIThinking || !aiColor || turn !== aiColor) return;

  isAIThinking = true;

  const turnEl = document.getElementById("current-turn");
  if (turnEl) {
    turnEl.innerText = `${AI_LEVELS[aiLevel].name} đang suy nghĩ...`;
  }

  setTimeout(() => {
    try {
      const bestMove = findBestMove(board, aiColor, aiLevel);

      if (bestMove) {
        // Lưu lịch sử
        moveHistory.push({
          board: board.map(row => [...row]),
          turn: turn,
          capturedWhite: [...capturedWhite],
          capturedBlack: [...capturedBlack]
        });

        const [fr, fc] = bestMove.from;
        const [tr, tc] = bestMove.to;

        // Bắt quân nếu có
      if (board[tr][tc] !== "") {
          // Lấy quân cờ bị bắt
          const capturedPiece = board[tr][tc]; 
          
          // Kiểm tra xem quân bị bắt có phải là quân Trắng (ký tự in hoa) không
          if (capturedPiece === capturedPiece.toUpperCase()) {
              // Nếu quân bị bắt là quân Trắng (W), thì người chơi quân Đen (B) bắt
              capturedWhite.push(capturedPiece); 
          } else {
              // Nếu quân bị bắt là quân Đen (ký tự in thường)
              capturedBlack.push(capturedPiece); 
          }
      }
      

        // Di chuyển quân trên bàn cờ thật
        board[tr][tc] = board[fr][fc];
        board[fr][fc] = "";

        // Đổi lượt
        turn = turn === "white" ? "black" : "white";

        // Vẽ lại và cập nhật UI
        drawBoard();
        updateTurn();

        // Nếu bạn có hàm updateBoard chỉ để log/hiển thị nước đi, truyền đúng bestMove
        // Nếu không cần, có thể xóa dòng này.
        // updateBoard(bestMove);

        console.log("AI moved:", bestMove);
      }

      // Cập nhật lại label lượt nếu cần
      if (turnEl) {
        turnEl.innerText = turn === "white" ? "Lượt Trắng" : "Lượt Đen";
      }
    } finally {
      isAIThinking = false;
    }
  }, 500);
}


function findBestMove(board, aiColor, level) {
  const config = AI_LEVELS[level];
  const moves = getAllMovesForAI(board, aiColor);
  
  if (moves.length === 0) return null;
  
  const moveEvaluations = [];
  
  console.log(`AI đang tính toán với depth=${config.depth}...`);
  
  for (const move of moves) {
    const newBoard = makeMoveAI(board, move.from, move.to);
    const value = minimax(
      newBoard, 
      config.depth - 1, 
      -Infinity, 
      Infinity, 
      aiColor === "white", 
      aiColor
    );  
    
    moveEvaluations.push({ move, value });
  }
  
  moveEvaluations.sort((a, b) => {
    return aiColor === "black" ? b.value - a.value : a.value - b.value;
  });
  
  console.log(`Tìm được ${moveEvaluations.length} nước đi, tốt nhất: ${moveEvaluations[0].value}`);
  
  let bestMove;
  if (config.randomness > 0 && Math.random() < config.randomness) {
    const topMoves = moveEvaluations.slice(0, Math.min(5, moveEvaluations.length));
    bestMove = topMoves[Math.floor(Math.random() * topMoves.length)].move;
  } else {
    bestMove = moveEvaluations[0].move;
  }
  
  return bestMove;
}

// ================= INITIALIZE =================
document.addEventListener("DOMContentLoaded", ()=>{
  chooseColorModal.classList.add("active");

  btnWhite.onclick = ()=> selectColorWithAI("white");
  btnBlack.onclick = ()=> selectColorWithAI("black");

  btnRestart.onclick = ()=> {
    chooseColorModal.classList.add("active");
  };

  btnUndo.onclick = ()=>{
    if(moveHistory.length > 0){
      const last = moveHistory.pop();
      board = last.board.map(r=>[...r]);
      turn = last.turn;
      capturedWhite = [...last.capturedWhite];
      capturedBlack = [...last.capturedBlack];
      selected = null;
      legalMoves = [];
      drawBoard();
      updateTurn();
    }
  };

  btnRules.onclick = ()=> rulesModal.classList.add("active");
  /*rulesClose.onclick = ()=> rulesModal.classList.remove("active");*/
  
  window.onclick = (e)=>{
    if(e.target === rulesModal) rulesModal.classList.remove("active");
    if(e.target === timeupModal) timeupModal.classList.remove("active");
  };

  btnTimeUp.onclick = ()=> { timer += 60; updateTimerDisplay(); };
  btnTimeDown.onclick = ()=> { if(timer > 60) timer -= 60; updateTimerDisplay(); };
  btnTimeStart.onclick = ()=> startTimer();
  btnTimePause.onclick = ()=> pauseTimer();
  btnTimeReset.onclick = ()=> resetTimer();

  closeTimeupModal.onclick = ()=>{
    timeupModal.classList.remove("active");
    resetTimer();
    startTimer();
  };

  toggleHint.onchange = ()=> {
    hintEnabled = toggleHint.checked;
    if(!hintEnabled){
      legalMoves = [];
      highlightMoves();
    }
  };

  updateTimerDisplay();
  
  // Thêm dropdown chọn AI level
  const aiSelect = document.getElementById("ai-level");
  if (aiSelect) {
    aiSelect.onchange = (e) => {
      aiLevel = parseInt(e.target.value);
      console.log(`Đã chọn cấp độ: ${AI_LEVELS[aiLevel].name}`);
    };
  }
});

// ================= BOARD LOGIC =================
function initBoard(){
  if(boardOrientation === "black"){
    board = [
      ["R","N","B","K","Q","B","N","R"],
      ["P","P","P","P","P","P","P","P"],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["p","p","p","p","p","p","p","p"],
      ["r","n","b","k","q","b","n","r"]
    ];
    turn = "black";
  } else {
    board = [
      ["r","n","b","q","k","b","n","r"],
      ["p","p","p","p","p","p","p","p"],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["","","","","","","",""],
      ["P","P","P","P","P","P","P","P"],
      ["R","N","B","Q","K","B","N","R"]
    ];
    turn = "white";
  }
  selected = null;
  legalMoves = [];
  capturedWhite = [];
  capturedBlack = [];
  moveHistory = [];
  drawBoard();
  updateTurn();
  updateCaptured();
  
  // Nếu AI đi trước
  if (aiColor === "white" && turn === "white") {
    setTimeout(() => makeAIMove(), 1000);
  }
}

// ================= DRAW BOARD =================
function drawBoard(){
  chessboard.innerHTML = "";
  let rows = [...Array(8).keys()];
  let cols = [...Array(8).keys()];

  for(let r of rows){
    for(let c of cols){
      const sq = document.createElement("div");
      sq.className = "square " + ((r+c)%2===0?"light":"dark");
      sq.dataset.row = r;
      sq.dataset.col = c;
      
      if(board[r][c] !== "") {
        sq.innerHTML = `<span class="piece">${PIECE_MAP[board[r][c]]}</span>`;
      }
      
      sq.addEventListener("click", ()=>handleClick(r,c));
      chessboard.appendChild(sq);
    }
  }
  
  highlightMoves();
  updateCaptured();
}

// ================= HANDLE CLICK =================
function addCaptured(piece){
    if(piece === piece.toUpperCase()) capturedWhite.push(piece);
    else capturedBlack.push(piece);
    updateCaptured();
}

function handleClick(r,c){
  if (isAIThinking) return;
  
  const piece = board[r][c];
  
  // Không cho chọn quân của AI
  if (piece && aiColor) {
    const isWhite = piece === piece.toUpperCase();
    const pieceColor = isWhite ? "white" : "black";
    if (pieceColor === aiColor) return;
  }
  
  if(piece && !selected){
    if((piece.toUpperCase()===piece && turn!=="white") || 
       (piece.toLowerCase()===piece && turn!=="black")) return;
    
    selected = {r,c};
    legalMoves = hintEnabled ? getMoves(r,c) : [];
    highlightMoves();
    return;
  }
  
  if(selected){
    const allMoves = getMoves(selected.r, selected.c);
    const moveValid = allMoves.some(m=>m[0]===r && m[1]===c);
    
    if(moveValid){
      moveHistory.push({
        board: board.map(row=>[...row]),
        turn: turn,
        capturedWhite: [...capturedWhite],
        capturedBlack: [...capturedBlack]
      });
      
      if(board[r][c] !== "") addCaptured(board[r][c]);
      
      board[r][c] = board[selected.r][selected.c];
      board[selected.r][selected.c] = "";
      
      turn = turn === "white" ? "black" : "white";
      selected = null;
      legalMoves = [];
      
      drawBoard();
      updateTurn();
      
      // AI đi
      if (aiColor && turn === aiColor) {
        setTimeout(() => makeAIMove(), 800);
      }
    } else {
      selected = null;
      legalMoves = [];
      highlightMoves();
    }
  }
}

function updateCaptured(){
  document.getElementById("captured-white").innerHTML = 
    capturedWhite.map(p=>PIECE_MAP[p]).join(" ");
  document.getElementById("captured-black").innerHTML = 
    capturedBlack.map(p=>PIECE_MAP[p]).join(" ");
}

function highlightMoves(){
  document.querySelectorAll(".square.selected, .square.highlight")
    .forEach(s=>s.classList.remove("selected","highlight"));
  
  if(hintEnabled){
    legalMoves.forEach(([r,c])=>{
      const sq = document.querySelector(`[data-row='${r}'][data-col='${c}']`);
      if(sq) sq.classList.add("highlight");
    });
  }
  
  if(selected){
    const selSq = document.querySelector(`[data-row='${selected.r}'][data-col='${selected.c}']`);
    if(selSq) selSq.classList.add("selected");
  }
}

// ================= MOVE LOGIC =================
function isOpponent(p1, p2){
    if(!p1 || !p2) return false;
    return (p1.toUpperCase()===p1 && p2.toLowerCase()===p2) || // p1 Trắng, p2 Đen
           (p1.toLowerCase()===p1 && p2.toUpperCase()===p2);  // p1 Đen, p2 Trắng
}

function getMoves(r, c){
    const piece = board[r][c];
    if(!piece) return [];

    const isWhite = piece === piece.toUpperCase();
    if((isWhite && turn !== "white") || (!isWhite && turn !== "black")) return [];

    let moves = [];
    let dir = isWhite ? -1 : 1;   // hướng đi của pawn
    let startRow = isWhite ? 6 : 1;

    switch(piece.toLowerCase()){
        case "p": // pawn
            // tiến thẳng 1 ô
            if(board[r+dir] && board[r+dir][c]==="") moves.push([r+dir,c]);
            // tiến thẳng 2 ô từ vị trí xuất phát
            if(r===startRow && board[r+dir][c]==="" && board[r+2*dir][c]==="") moves.push([r+2*dir,c]);
            // ăn chéo
            if(board[r+dir] && board[r+dir][c-1]!==undefined && board[r+dir][c-1]!=="") 
                if(isOpponent(piece, board[r+dir][c-1])) moves.push([r+dir,c-1]);
            if(board[r+dir] && board[r+dir][c+1]!==undefined && board[r+dir][c+1]!=="") 
                if(isOpponent(piece, board[r+dir][c+1])) moves.push([r+dir,c+1]);
            break;

        case "r": moves = directions(board,r,c,[[1,0],[-1,0],[0,1],[0,-1]]); break;
        case "b": moves = directions(board,r,c,[[1,1],[1,-1],[-1,1],[-1,-1]]); break;
        case "q": moves = directions(board,r,c,[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]); break;
        case "n": moves = knightMoves(board,r,c); break;
        case "k": moves = kingMoves(board,r,c); break;
    }

    return moves;
}

function getMovesForAI(board,r,c){
    const piece = board[r][c];
    if(!piece) return [];
    const isWhite = piece === piece.toUpperCase();

    if(piece.toLowerCase() === "p"){
        const moves = [];
        const step = isWhite ? -1 : 1;
        const startRow = isWhite ? 6 : 1;

        if(board[r+step] && board[r+step][c]==="") moves.push([r+step,c]);
        if(r===startRow && board[r+step][c]==="" && board[r+2*step][c]==="") moves.push([r+2*step,c]);
        if(board[r+step] && board[r+step][c-1]!==undefined && isOpponent(piece, board[r+step][c-1])) moves.push([r+step,c-1]);
        if(board[r+step] && board[r+step][c+1]!==undefined && isOpponent(piece, board[r+step][c+1])) moves.push([r+step,c+1]);

        return moves;
    } else {
        switch(piece.toLowerCase()){
            case "r": return directions(board,r,c,[[1,0],[-1,0],[0,1],[0,-1]]);
            case "b": return directions(board,r,c,[[1,1],[1,-1],[-1,1],[-1,-1]]);
            case "q": return directions(board,r,c,[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]);
            case "n": return knightMoves(board,r,c);
            case "k": return kingMoves(board,r,c);
        }
    }
    return [];
}

function directions(board, r, c, dirs){
    let moves = [];
    for(let [dr, dc] of dirs){
        let nr = r + dr, nc = c + dc;
        while(nr >= 0 && nr < 8 && nc >= 0 && nc < 8){
            if(board[nr][nc] === ""){
                moves.push([nr, nc]);
            } else {
                if(isOpponent(board[r][c], board[nr][nc])){
                    moves.push([nr, nc]); // có thể ăn
                }
                break; 
            }
            nr += dr;
            nc += dc;
        }
    }
    return moves;
}


function knightMoves(board, r, c){
    const deltas = [[2,1],[2,-1],[-2,1],[-2,-1],[1,2],[1,-2],[-1,2],[-1,-2]];
    let moves = [];
    for(let [dr, dc] of deltas){
        const nr = r + dr, nc = c + dc;
        if(nr >= 0 && nr < 8 && nc >= 0 && nc < 8){
            if(board[nr][nc] === "" || isOpponent(board[r][c], board[nr][nc])){
                moves.push([nr, nc]);
            }
        }
    }
    return moves;
}

function kingMoves(board, r, c){
    let moves = [];
    for(let dr=-1; dr<=1; dr++){
        for(let dc=-1; dc<=1; dc++){
            if(dr===0 && dc===0) continue;
            const nr = r + dr, nc = c + dc;
            if(nr >= 0 && nr < 8 && nc >= 0 && nc < 8){
                if(board[nr][nc] === "" || isOpponent(board[r][c], board[nr][nc])){
                    moves.push([nr, nc]);
                }
            }
        }
    }
    return moves;
}


// ================= UI =================
function updateTurn(){
  const turnEl = document.getElementById("current-turn");
  if (turnEl) {
    turnEl.innerText = turn === "white" ? "Đến lượt quân Trắng" : "Đến lượt quân Đen";
  }
}


// ================= TIMER =================
function updateTimerDisplay(){
  let min = Math.floor(timer/60);
  let sec = timer % 60;
  timerDisplay.textContent = `${min}:${sec.toString().padStart(2,'0')}`;
}

function startTimer(){ 
  if(timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(()=>{ 
    if(timer > 0){
      timer--;
      updateTimerDisplay();
    } else { 
      clearInterval(timerInterval); 
      showTimeupModal(); 
    } 
  }, 1000);
}

function pauseTimer(){ 
  if(timerInterval) clearInterval(timerInterval); 
}

function resetTimer(){ 
  pauseTimer(); 
  timer = 300; 
  updateTimerDisplay(); 
}

function showTimeupModal(){
  timeupModal.classList.add("active");
  pauseTimer();
}

function selectColorWithAI(color)
{ 
  playerColor = color;
  aiColor = color === "white" ? "black" : "white";
  chooseColorModal.classList.remove("active");
  boardOrientation = color;
  initBoard();
  
  console.log(`Người chơi: ${playerColor}, AI: ${aiColor}, Cấp độ: ${AI_LEVELS[aiLevel].name}`);
}

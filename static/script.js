// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    // Screen containers
    const setupScreen = document.getElementById('setup-screen');
    const gameContainer = document.getElementById('game-container');

    // Setup elements
    const startGameButton = document.getElementById('start-game-button');
    const backToSetupButton = document.getElementById('back-to-setup-button');

    // Game elements
    const boardElement = document.getElementById('board');
    const messageElement = document.getElementById('message');
    const titleElement = document.getElementById('game-title');
    const scoreboardElement = document.getElementById('scoreboard');
    const resetButton = document.getElementById('reset-button');
    const resetScoreButton = document.getElementById('reset-score-button');

    const PLAYER_COLORS = ['red', 'gold', 'blue', 'green'];
    let currentBoardState = { rows: 0, cols: 0 };

    function createBoard(rows, cols) {
        // Only recreate the board if the size has changed
        if (currentBoardState.rows === rows && currentBoardState.cols === cols) {
            return;
        }
        currentBoardState = { rows, cols };
        
        boardElement.innerHTML = '';
        // Use CSS variables to control grid layout
        document.documentElement.style.setProperty('--cols', cols);

        for (let c = 0; c < cols; c++) {
            const column = document.createElement('div');
            column.classList.add('column');
            column.addEventListener('click', () => handleColumnClick(c));
            for (let r = 0; r < rows; r++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.row = r;
                cell.dataset.col = c;
                column.appendChild(cell);
            }
            boardElement.appendChild(column);
        }
    }

    function updateUI(state) {
        if (state.setup_mode) {
            setupScreen.style.display = 'flex';
            gameContainer.style.display = 'none';
            return;
        }
        
        setupScreen.style.display = 'none';
        gameContainer.style.display = 'flex';

        // Update Title
        titleElement.textContent = `Connect ${state.connect_n}`;

        // Update Scoreboard Dynamically
        scoreboardElement.innerHTML = '';
        for (let i = 1; i <= state.num_players; i++) {
            const scoreBox = document.createElement('div');
            scoreBox.classList.add('score');
            scoreBox.id = `score-${i}`;
            scoreBox.innerHTML = `${PLAYER_COLORS[i-1].charAt(0).toUpperCase() + PLAYER_COLORS[i-1].slice(1)}: <span id="score-val-${i}">${state.scores[i] || 0}</span>`;
            scoreboardElement.appendChild(scoreBox);
        }

        // Create or verify board size
        createBoard(state.rows, state.cols);
        
        // Update message and board state
        messageElement.textContent = state.message;
        const cells = document.querySelectorAll('.cell');
        cells.forEach(cell => {
            const r = parseInt(cell.dataset.row);
            const c = parseInt(cell.dataset.col);
            const player = state.board[r][c];
            
            cell.className = 'cell'; // Reset classes
            if (player > 0) {
                cell.classList.add(PLAYER_COLORS[player - 1]);
            }
        });
        
        boardElement.style.pointerEvents = state.game_over ? 'none' : 'auto';
    }

    async function sendRequest(endpoint, body = null) {
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(endpoint, options);
        const state = await response.json();
        updateUI(state);
    }

    function handleColumnClick(col) { sendRequest('/move', { column: col }); }
    function resetGame() { sendRequest('/reset'); }
    function resetScore() { sendRequest('/reset_score'); }

    startGameButton.addEventListener('click', () => {
        const players = document.querySelector('input[name="players"]:checked').value;
        const connect = document.querySelector('input[name="connect"]:checked').value;
        sendRequest('/start', { players, connect });
    });

    backToSetupButton.addEventListener('click', () => {
        setupScreen.style.display = 'flex';
        gameContainer.style.display = 'none';
    });

    // --- Initial Load ---
    fetch('/state').then(res => res.json()).then(updateUI);
});
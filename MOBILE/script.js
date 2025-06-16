// Game Setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Responsive canvas setup
function resizeCanvas() {
    const container = document.getElementById('gameContainer');
    const rect = container.getBoundingClientRect();
    canvas.width = Math.min(400, rect.width);
    canvas.height = Math.min(600, rect.height);
}

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Game Constants
const COLORS = {
    SKY_BLUE: '#87CEEB',
    CLOUD_WHITE: '#FFFFFF',
    PLATFORM_GREEN: '#228B22',
    PLATFORM_DARK: '#006400',
    PLATFORM_SPECIAL: '#FFD700',
    PLATFORM_MOVING: '#6464FF',
    PLAYER_BLUE: '#1E90FF',
    PLAYER_RED: '#DC143C',
    PLAYER_YELLOW: '#FFD700',
    PLAYER_BROWN: '#8B4513',
    PLAYER_SKIN: '#FFE4B5',
    UI_WHITE: '#FFFFFF',
    UI_BLACK: '#000000',
    SHADOW_GRAY: '#C8C8C8',
    COIN_GOLD: '#FFD700',
    POWER_UP_PURPLE: '#9300D3'
};

// Game States
const GAME_STATES = {
    MENU: 0,
    PLAYING: 1,
    GAME_OVER: 2
};

// Game Variables
let gameState = GAME_STATES.MENU;
let timeCounter = 0;
let score = 0;
let highScore = parseInt(localStorage.getItem('highScore') || '0');
let coinCount = 0;

// Player
const player = {
    x: canvas.width / 2,
    y: canvas.height - 100,
    width: 40,
    height: 48,
    vy: 0,
    facingRight: true,
    animationFrame: 0
};

const PHYSICS = {
    gravity: 0.5,
    jumpStrength: -15,
    moveSpeed: 6
};

// Game Objects
let platforms = [];
let coins = [];
let powerUps = [];
let particles = [];
let clouds = [];

// Initialize clouds
for (let i = 0; i < 8; i++) {
    clouds.push({
        x: Math.random() * (canvas.width + 100) - 50,
        y: Math.random() * (canvas.height - 100) + 50,
        size: Math.random() * 40 + 40,
        speed: Math.random() * 0.6 + 0.2
    });
}

// Platform Class
class Platform {
    constructor(x, y, width, height, type = 'normal') {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.type = type;
        this.originalX = x;
        this.moveRange = 100;
        this.moveSpeed = 1;
        this.direction = 1;
    }

    update() {
        if (this.type === 'moving') {
            this.x += this.moveSpeed * this.direction;
            if (this.x > this.originalX + this.moveRange || this.x < this.originalX - this.moveRange) {
                this.direction *= -1;
            }
        }
    }

    draw() {
        // Shadow
        ctx.fillStyle = COLORS.SHADOW_GRAY;
        ctx.fillRect(this.x + 2, this.y + 2, this.width, this.height);

        // Platform based on type
        if (this.type === 'bounce') {
            ctx.fillStyle = COLORS.PLATFORM_SPECIAL;
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.strokeStyle = COLORS.UI_BLACK;
            ctx.lineWidth = 2;
            ctx.strokeRect(this.x, this.y, this.width, this.height);

            // Spring symbol
            ctx.strokeStyle = COLORS.UI_BLACK;
            ctx.lineWidth = 3;
            const centerX = this.x + this.width / 2;
            ctx.beginPath();
            ctx.moveTo(centerX - 10, this.y + 5);
            ctx.lineTo(centerX + 10, this.y + 5);
            ctx.stroke();
        } else if (this.type === 'moving') {
            ctx.fillStyle = COLORS.PLATFORM_MOVING;
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.strokeStyle = COLORS.UI_BLACK;
            ctx.lineWidth = 2;
            ctx.strokeRect(this.x, this.y, this.width, this.height);

            // Arrow symbols
            ctx.fillStyle = COLORS.UI_WHITE;
            ctx.beginPath();
            ctx.moveTo(this.x + 10, this.y + this.height / 2);
            ctx.lineTo(this.x + 20, this.y + this.height / 2 - 5);
            ctx.lineTo(this.x + 20, this.y + this.height / 2 + 5);
            ctx.fill();
        } else {
            ctx.fillStyle = COLORS.PLATFORM_GREEN;
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.strokeStyle = COLORS.PLATFORM_DARK;
            ctx.lineWidth = 2;
            ctx.strokeRect(this.x, this.y, this.width, this.height);

            // Grass texture
            ctx.strokeStyle = '#3CB371';
            ctx.lineWidth = 2;
            for (let grassX = this.x + 5; grassX < this.x + this.width - 5; grassX += 8) {
                ctx.beginPath();
                ctx.moveTo(grassX, this.y);
                ctx.lineTo(grassX, this.y - 3);
                ctx.stroke();
            }
        }
    }

    collidesWith(rect) {
        return rect.x < this.x + this.width &&
            rect.x + rect.width > this.x &&
            rect.y < this.y + this.height &&
            rect.y + rect.height > this.y;
    }
}

// Coin Class
class Coin {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.animation = 0;
        this.collected = false;
    }

    update() {
        this.animation += 0.2;
    }

    draw() {
        if (!this.collected) {
            const size = 12 + Math.sin(this.animation) * 2;
            ctx.fillStyle = COLORS.COIN_GOLD;
            ctx.beginPath();
            ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.UI_BLACK;
            ctx.lineWidth = 2;
            ctx.stroke();

            // $ symbol
            ctx.fillStyle = COLORS.UI_BLACK;
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('$', this.x, this.y + 4);
        }
    }

    collidesWith(rect) {
        const dx = this.x - (rect.x + rect.width / 2);
        const dy = this.y - (rect.y + rect.height / 2);
        return Math.sqrt(dx * dx + dy * dy) < 20;
    }
}

// Particle Class
class Particle {
    constructor(x, y, color, vx, vy) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.vx = vx;
        this.vy = vy;
        this.life = 30;
        this.maxLife = 30;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += 0.1;
        this.life--;
    }

    draw() {
        if (this.life > 0) {
            const size = Math.max(1, 4 * (this.life / this.maxLife));
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

// Utility Functions
function createJumpParticles(x, y) {
    for (let i = 0; i < 6; i++) {
        const vx = (Math.random() - 0.5) * 4;
        const vy = Math.random() * -2;
        const colors = [COLORS.PLATFORM_GREEN, COLORS.UI_WHITE, COLORS.SKY_BLUE];
        const color = colors[Math.floor(Math.random() * colors.length)];
        particles.push(new Particle(x, y, color, vx, vy));
    }
}

function createCoinParticles(x, y) {
    for (let i = 0; i < 8; i++) {
        const vx = (Math.random() - 0.5) * 6;
        const vy = Math.random() * -2 - 1;
        particles.push(new Particle(x, y, COLORS.COIN_GOLD, vx, vy));
    }
}

// Drawing Functions
function drawCloud(x, y, size) {
    ctx.fillStyle = COLORS.CLOUD_WHITE;
    ctx.beginPath();
    ctx.arc(x, y, size * 0.6, 0, Math.PI * 2);
    ctx.arc(x - size * 0.4, y, size * 0.4, 0, Math.PI * 2);
    ctx.arc(x + size * 0.4, y, size * 0.4, 0, Math.PI * 2);
    ctx.arc(x - size * 0.2, y - size * 0.3, size * 0.35, 0, Math.PI * 2);
    ctx.arc(x + size * 0.2, y - size * 0.3, size * 0.35, 0, Math.PI * 2);
    ctx.fill();
}

function drawBackground() {
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, COLORS.SKY_BLUE);
    gradient.addColorStop(1, '#E0F6FF');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw clouds
    clouds.forEach(cloud => {
        drawCloud(cloud.x, cloud.y, cloud.size);
        cloud.x += cloud.speed;
        if (cloud.x > canvas.width + cloud.size) {
            cloud.x = -cloud.size;
        }
    });
}

function drawPlayer() {
    const x = player.x;
    const y = player.y;

    // Shadow
    ctx.fillStyle = COLORS.SHADOW_GRAY;
    ctx.fillRect(x + 4, y + player.height - 4, player.width - 8, 8);

    // Feet
    ctx.fillStyle = COLORS.PLAYER_BROWN;
    ctx.fillRect(x + 2, y + 40, 12, 8);
    ctx.fillRect(x + 26, y + 40, 12, 8);

    // Legs
    ctx.fillStyle = COLORS.PLAYER_BLUE;
    ctx.fillRect(x + 8, y + 28, 24, 16);

    // Body
    ctx.fillStyle = COLORS.PLAYER_RED;
    ctx.fillRect(x + 4, y + 16, 32, 20);

    // Suspenders
    ctx.fillStyle = COLORS.PLAYER_YELLOW;
    ctx.fillRect(x + 12, y + 18, 6, 12);
    ctx.fillRect(x + 22, y + 18, 6, 12);

    // Head
    ctx.fillStyle = COLORS.PLAYER_SKIN;
    ctx.fillRect(x + 8, y + 4, 24, 20);

    // Hat
    ctx.fillStyle = COLORS.PLAYER_RED;
    ctx.fillRect(x + 6, y, 28, 12);

    // Hat brim
    if (player.facingRight) {
        ctx.fillRect(x + 30, y + 6, 8, 6);
    } else {
        ctx.fillRect(x + 2, y + 6, 8, 6);
    }

    // Eyes
    ctx.fillStyle = COLORS.UI_BLACK;
    ctx.beginPath();
    ctx.arc(x + 16, y + 12, 3, 0, Math.PI * 2);
    ctx.arc(x + 24, y + 12, 3, 0, Math.PI * 2);
    ctx.fill();

    // Pupils
    ctx.fillStyle = COLORS.UI_WHITE;
    ctx.beginPath();
    if (player.facingRight) {
        ctx.arc(x + 17, y + 11, 1, 0, Math.PI * 2);
        ctx.arc(x + 25, y + 11, 1, 0, Math.PI * 2);
    } else {
        ctx.arc(x + 15, y + 11, 1, 0, Math.PI * 2);
        ctx.arc(x + 23, y + 11, 1, 0, Math.PI * 2);
    }
    ctx.fill();

    // Mustache
    ctx.fillStyle = COLORS.PLAYER_BROWN;
    ctx.fillRect(x + 14, y + 18, 12, 3);

    // "M" on hat
    ctx.fillStyle = COLORS.UI_WHITE;
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('M', x + 20, y + 8);
}

// Game Logic
function resetGame() {
    player.x = canvas.width / 2 - player.width / 2;
    player.y = canvas.height - 100;
    player.vy = 0;
    score = 0;
    coinCount = 0;

    platforms = [];
    coins = [];
    powerUps = [];
    particles = [];

    // Start platform
    platforms.push(new Platform(canvas.width / 2 - 60, canvas.height - 60, 120, 20, 'normal'));

    // Generate initial platforms
    for (let i = 1; i < 8; i++) {
        const x = Math.random() * (canvas.width - 100);
        const y = canvas.height - i * 80;
        const width = Math.random() * 40 + 80;

        let type = 'normal';
        const rand = Math.random();
        if (rand < 0.2) type = 'bounce';
        else if (rand < 0.3) type = 'moving';

        platforms.push(new Platform(x, y, width, 20, type));
    }
}

function spawnCollectibles() {
    platforms.forEach(platform => {
        const hasNearbyCoin = coins.some(coin =>
            Math.abs(coin.x - (platform.x + platform.width / 2)) < 50 &&
            Math.abs(coin.y - platform.y) < 50
        );

        if (!hasNearbyCoin && Math.random() < 0.05) {
            const coinX = platform.x + Math.random() * (platform.width - 20) + 10;
            const coinY = platform.y - 20;
            coins.push(new Coin(coinX, coinY));
        }
    });
}

function updateGame() {
    if (gameState !== GAME_STATES.PLAYING) return;

    timeCounter++;

    // Update platforms
    platforms.forEach(platform => platform.update());

    // Physics
    player.vy += PHYSICS.gravity;
    player.y += player.vy;

    // Platform collision
    if (player.vy > 0) {
        const playerRect = {
            x: player.x,
            y: player.y,
            width: player.width,
            height: player.height
        };

        platforms.forEach(platform => {
            if (platform.collidesWith(playerRect) && player.y + player.height <= platform.y + player.vy + 10) {
                player.y = platform.y - player.height;

                if (platform.type === 'bounce') {
                    player.vy = PHYSICS.jumpStrength * 1.5;
                } else {
                    player.vy = PHYSICS.jumpStrength;
                }

                createJumpParticles(player.x + player.width / 2, player.y + player.height);
            }
        });
    }

    // Collect coins
    coins.forEach((coin, index) => {
        coin.update();
        if (!coin.collected && coin.collidesWith(player)) {
            coin.collected = true;
            coinCount++;
            score += 50;
            createCoinParticles(coin.x, coin.y);
            coins.splice(index, 1);
        }
    });

    // Update particles
    particles.forEach((particle, index) => {
        particle.update();
        if (particle.life <= 0) {
            particles.splice(index, 1);
        }
    });

    // Camera effect
    if (player.y < canvas.height / 2) {
        const offset = canvas.height / 2 - player.y;
        player.y = canvas.height / 2;
        score += offset * 0.1;

        platforms.forEach(platform => {
            platform.y += offset;
            platform.originalX = platform.x; // Update for moving platforms
        });

        coins.forEach(coin => {
            coin.y += offset;
        });

        particles.forEach(particle => {
            particle.y += offset;
        });
    }

    // Generate new platforms
    while (platforms.length < 12) {
        const lastY = Math.min(...platforms.map(p => p.y));
        const newX = Math.random() * (canvas.width - 120);
        const newY = lastY - (Math.random() * 40 + 60);
        const width = Math.random() * 40 + 80;

        let type = 'normal';
        const rand = Math.random();
        if (rand < 0.2) type = 'bounce';
        else if (rand < 0.3) type = 'moving';

        platforms.push(new Platform(newX, newY, width, 20, type));
    }

    // Spawn collectibles
    if (timeCounter % 60 === 0) {
        spawnCollectibles();
    }

    // Remove off-screen objects
    platforms = platforms.filter(p => p.y < canvas.height + 50);
    coins = coins.filter(c => c.y < canvas.height + 100);

    // Game over
    if (player.y > canvas.height) {
        if (score > highScore) {
            highScore = score;
            localStorage.setItem('highScore', highScore.toString());
        }
        gameState = GAME_STATES.GAME_OVER;
        updateUI();
        showGameOverScreen();
    }

    updateUI();
}

function updateUI() {
    document.getElementById('scoreDisplay').textContent = Math.floor(score);
    document.getElementById('coinDisplay').textContent = coinCount;
    document.getElementById('highScoreDisplay').textContent = Math.floor(highScore);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (gameState === GAME_STATES.PLAYING) {
        drawBackground();

        // Draw platforms
        platforms.forEach(platform => platform.draw());

        // Draw coins
        coins.forEach(coin => coin.draw());

        // Draw particles
        particles.forEach(particle => particle.draw());

        // Draw player
        drawPlayer();
    }
}

function gameLoop() {
    updateGame();
    draw();
    requestAnimationFrame(gameLoop);
}

// UI Management
function showMenuScreen() {
    document.getElementById('menuScreen').classList.remove('hidden');
    document.getElementById('gameOverScreen').classList.add('hidden');
    document.getElementById('gameUI').classList.add('hidden');
    document.getElementById('gameControls').classList.add('hidden');
}

function showGameScreen() {
    document.getElementById('menuScreen').classList.add('hidden');
    document.getElementById('gameOverScreen').classList.add('hidden');
    document.getElementById('gameUI').classList.remove('hidden');
    document.getElementById('gameControls').classList.remove('hidden');
}

function showGameOverScreen() {
    document.getElementById('finalScore').textContent = Math.floor(score);
    document.getElementById('finalCoins').textContent = coinCount;
    document.getElementById('finalHighScore').textContent = Math.floor(highScore);

    document.getElementById('gameOverScreen').classList.remove('hidden');
    document.getElementById('gameUI').classList.add('hidden');
    document.getElementById('gameControls').classList.add('hidden');
}

// Input Handling
let leftPressed = false;
let rightPressed = false;

function handleInput() {
    if (gameState === GAME_STATES.PLAYING) {
        if (leftPressed) {
            player.x -= PHYSICS.moveSpeed;
            player.facingRight = false;
        }
        if (rightPressed) {
            player.x += PHYSICS.moveSpeed;
            player.facingRight = true;
        }

        // Screen wrapping
        if (player.x + player.width < 0) {
            player.x = canvas.width;
        } else if (player.x > canvas.width) {
            player.x = -player.width;
        }
    }
}

setInterval(handleInput, 16); // 60 FPS input handling

// Event Listeners
document.getElementById('startBtn').addEventListener('click', () => {
    gameState = GAME_STATES.PLAYING;
    resetGame();
    showGameScreen();
});

document.getElementById('restartBtn').addEventListener('click', () => {
    gameState = GAME_STATES.PLAYING;
    resetGame();
    showGameScreen();
});

document.getElementById('menuBtn').addEventListener('click', () => {
    gameState = GAME_STATES.MENU;
    showMenuScreen();
});

// Touch Controls
document.getElementById('leftBtn').addEventListener('touchstart', (e) => {
    e.preventDefault();
    leftPressed = true;
});

document.getElementById('leftBtn').addEventListener('touchend', (e) => {
    e.preventDefault();
    leftPressed = false;
});

document.getElementById('leftBtn').addEventListener('touchcancel', (e) => {
    e.preventDefault();
    leftPressed = false;
});

document.getElementById('rightBtn').addEventListener('touchstart', (e) => {
    e.preventDefault();
    rightPressed = true;
});

document.getElementById('rightBtn').addEventListener('touchend', (e) => {
    e.preventDefault();
    rightPressed = false;
});

document.getElementById('rightBtn').addEventListener('touchcancel', (e) => {
    e.preventDefault();
    rightPressed = false;
});

// Mouse Controls for desktop
document.getElementById('leftBtn').addEventListener('mousedown', (e) => {
    e.preventDefault();
    leftPressed = true;
});

document.getElementById('leftBtn').addEventListener('mouseup', (e) => {
    e.preventDefault();
    leftPressed = false;
});

document.getElementById('rightBtn').addEventListener('mousedown', (e) => {
    e.preventDefault();
    rightPressed = true;
});

document.getElementById('rightBtn').addEventListener('mouseup', (e) => {
    e.preventDefault();
    rightPressed = false;
});

// Keyboard Controls
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
        leftPressed = true;
        e.preventDefault();
    }
    if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        rightPressed = true;
        e.preventDefault();
    }
    if ((e.key === ' ' || e.key === 'Enter') && gameState === GAME_STATES.MENU) {
        document.getElementById('startBtn').click();
        e.preventDefault();
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
        leftPressed = false;
        e.preventDefault();
    }
    if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        rightPressed = false;
        e.preventDefault();
    }
});

// Prevent context menu on long press
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});

// Initialize game
updateUI();
showMenuScreen();
gameLoop();

// Prevent zoom on double tap
let lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Handle orientation change
window.addEventListener('orientationchange', () => {
    setTimeout(() => {
        resizeCanvas();
    }, 100);
});
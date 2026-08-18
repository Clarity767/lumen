(function () {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const overlay = document.getElementById('gameOverlay');
    const startBtn = document.getElementById('startBtn');
    const retryBtn = document.getElementById('retryBtn');
    const scoreDisplay = document.getElementById('scoreDisplay');
    const resultBlock = document.getElementById('resultBlock');
    const promoResult = document.getElementById('promoResult');
    const noPromoResult = document.getElementById('noPromoResult');

    const GROUND_Y = 250;
    const GRAVITY = 0.7;
    const JUMP_FORCE = -13;

    let player, obstacles, score, speed, isRunning, animFrame, spawnTimer, runTick;

    function resetGame() {
        player = { x: 60, y: GROUND_Y, width: 30, height: 40, vy: 0, jumping: false };
        obstacles = [];
        score = 0;
        speed = 6;
        spawnTimer = 0;
        runTick = 0;
        isRunning = true;
        scoreDisplay.textContent = '0';
        resultBlock.style.display = 'none';
        promoResult.style.display = 'none';
        noPromoResult.style.display = 'none';
    }

    function spawnObstacle() {
        const height = 30 + Math.random() * 30;
        obstacles.push({ x: canvas.width, y: GROUND_Y + 40 - height, width: 20, height });
    }

    function update() {
        player.vy += GRAVITY;
        player.y += player.vy;
        if (player.y > GROUND_Y) {
            player.y = GROUND_Y;
            player.vy = 0;
            player.jumping = false;
        }

        spawnTimer++;
        const spawnRate = Math.max(40, 90 - Math.floor(score / 10));
        if (spawnTimer > spawnRate) {
            spawnObstacle();
            spawnTimer = 0;
        }

        obstacles.forEach(o => o.x -= speed);
        obstacles = obstacles.filter(o => o.x + o.width > 0);

        for (const o of obstacles) {
            if (player.x < o.x + o.width && player.x + player.width > o.x && player.y + player.height > o.y) {
                endGame();
                return;
            }
        }

        score += 1;
        if (score % 100 === 0) speed += 0.5;
        scoreDisplay.textContent = Math.floor(score / 5);
        if (!player.jumping) runTick++;
    }

    // ---- красивая отрисовка персонажа ----
    function drawPlayer() {
        const { x, y, width, height, jumping } = player;
        const cx = x + width / 2;
    
        // тень
        const jumpHeight = Math.max(0, GROUND_Y - y);
        const shadowScale = Math.max(0.3, 1 - jumpHeight / 120);
        ctx.save();
        ctx.globalAlpha = 0.3 * shadowScale;
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.ellipse(cx, GROUND_Y + height + 6, (width / 2) * shadowScale, 4 * shadowScale, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    
        const legPhase = jumping ? 0 : Math.sin(runTick * 0.4) * 6;
    
        ctx.save();
        ctx.translate(x, y);
    
        // ноги — светлые, с обводкой
        ctx.strokeStyle = '#F5E6C8';
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(width * 0.35, height - 10);
        ctx.lineTo(width * 0.35 + legPhase, height + (jumping ? -2 : 6));
        ctx.moveTo(width * 0.65, height - 10);
        ctx.lineTo(width * 0.65 - legPhase, height + (jumping ? -2 : 6));
        ctx.stroke();
    
        // тело — яркое золото + тёмная обводка для контраста на любом фоне
        const bodyGrad = ctx.createLinearGradient(0, 0, 0, height);
        bodyGrad.addColorStop(0, '#F5D98A');
        bodyGrad.addColorStop(1, '#E3B95C');
        ctx.fillStyle = bodyGrad;
        ctx.strokeStyle = '#141210';
        ctx.lineWidth = 2;
        roundRect(ctx, 2, 10, width - 4, height - 16, 8);
        ctx.fill();
        ctx.stroke();
    
        // голова
        ctx.fillStyle = '#F5E6C8';
        ctx.strokeStyle = '#141210';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(width / 2, 6, 9, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
    
        ctx.restore();
    }

    // ---- красивая отрисовка препятствия ----
    function drawObstacle(o) {
        const grad = ctx.createLinearGradient(o.x, o.y, o.x, o.y + o.height);
        grad.addColorStop(0, '#D4816E');   // светлее ember
        grad.addColorStop(1, '#A65B4A');
        ctx.fillStyle = grad;
        ctx.strokeStyle = '#141210';
        ctx.lineWidth = 2;
        roundRect(ctx, o.x, o.y, o.width, o.height, 4);
        ctx.fill();
        ctx.stroke();
    
        // блик сверху
        ctx.fillStyle = 'rgba(255,255,255,0.25)';
        roundRect(ctx, o.x + 2, o.y + 2, o.width - 4, 4, 2);
        ctx.fill();
    
        // тень
        ctx.save();
        ctx.globalAlpha = 0.3;
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.ellipse(o.x + o.width / 2, GROUND_Y + 46, o.width / 2, 3, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // земля с лёгкой текстурой вместо голой линии
        ctx.fillStyle = '#8b5e3c';
        ctx.fillRect(0, GROUND_Y + 40, canvas.width, 4);
        ctx.strokeStyle = 'rgba(139,94,60,0.4)';
        ctx.lineWidth = 1;
        for (let i = 0; i < canvas.width; i += 24) {
            const offset = (runTick * (isRunning ? speed : 0)) % 24;
            ctx.beginPath();
            ctx.moveTo(i - offset, GROUND_Y + 44);
            ctx.lineTo(i - offset - 10, GROUND_Y + 48);
            ctx.stroke();
        }

        drawPlayer();
        obstacles.forEach(drawObstacle);
    }

    function loop() {
        if (!isRunning) return;
        update();
        draw();
        animFrame = requestAnimationFrame(loop);
    }

    function jump() {
        if (!isRunning) return;
        if (!player.jumping) {
            player.vy = JUMP_FORCE;
            player.jumping = true;
        }
    }

    function endGame() {
        isRunning = false;
        cancelAnimationFrame(animFrame);
        submitScore(Math.floor(score / 5));
    }

    function submitScore(finalScore) {
        fetch(window.GAME_FINISH_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN },
            body: JSON.stringify({ score: finalScore }),
        })
            .then(res => res.json())
            .then(data => {
                resultBlock.style.display = 'block';
                if (data.promo) {
                    promoResult.style.display = 'block';
                    promoResult.innerHTML = `🎉 Вітаємо! Твій промокод: <strong>${data.promo.code}</strong><br>${data.promo.description}`;
                } else {
                    noPromoResult.style.display = 'block';
                }
            })
            .catch(() => {
                resultBlock.style.display = 'block';
                noPromoResult.style.display = 'block';
                noPromoResult.textContent = 'Помилка збереження результату. Спробуй ще раз.';
            });
    }
    function roundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
    }

    function startGame() {
        overlay.style.display = 'none';
        resetGame();
        draw();
        loop();
    }

    startBtn.addEventListener('click', startGame);
    retryBtn.addEventListener('click', startGame);
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') { e.preventDefault(); jump(); }
    });
    canvas.addEventListener('click', jump);
})();
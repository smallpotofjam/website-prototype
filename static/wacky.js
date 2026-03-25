const playArea = document.getElementById('play-area');
const toggleBtn = document.getElementById('toggle-btn');
const wackyImages = document.querySelectorAll('.wacky');

let running = true;
let animationId = null;

// Give each image a starting velocity and direction
const fishData = [];

wackyImages.forEach(img => {
  fishData.push({
    el: img,
    x: playArea.clientWidth / 2,
    y: playArea.clientHeight / 2,
    dx: (Math.random() * 2 + 1) * (Math.random() < 0.5 ? -1 : 1),
    dy: (Math.random() * 2 + 1) * (Math.random() < 0.5 ? -1 : 1),
    speed: Math.random() * 1.5 + 1.5
  });

  // PERMANENT FLIP (initial state)
  img.dataset.baseFlip = "-1"; // store permanent flip direction
  img.style.transform = "translate(-50%, -50%) scaleX(-1)";
});

function swim() {
  const areaWidth = playArea.clientWidth;
  const areaHeight = playArea.clientHeight;

  fishData.forEach(fish => {
    const img = fish.el;
    const w = img.clientWidth;
    const h = img.clientHeight;

    // Move fish
    fish.x += fish.dx * fish.speed;
    fish.y += fish.dy * fish.speed;

    // Bounce off walls
    if (fish.x < 0 || fish.x + w > areaWidth) {
      fish.dx *= -1;

      // Flip relative to permanent flip
      const base = img.dataset.baseFlip === "-1" ? -1 : 1;
      const directionFlip = fish.dx > 0 ? 1 : -1;

      img.style.transform =
        `translate(-50%, -50%) scaleX(${base * directionFlip})`;
    }

    if (fish.y < 0 || fish.y + h > areaHeight) {
      fish.dy *= -1;
    }

    // Apply position
    img.style.left = fish.x + "px";
    img.style.top = fish.y + "px";
  });

  if (running) {
    animationId = requestAnimationFrame(swim);
  }
}

function startSwimming() {
  if (!animationId) {
    running = true;
    animationId = requestAnimationFrame(swim);
  }
}

function stopSwimming() {
  running = false;
  cancelAnimationFrame(animationId);
  animationId = null;
}

toggleBtn.addEventListener('click', () => {
  running = !running;

  if (running) {
    toggleBtn.textContent = "Pause Wackiness";
    startSwimming();
  } else {
    toggleBtn.textContent = "Start Wackiness";
    stopSwimming();
  }
});

// Start automatically
startSwimming();

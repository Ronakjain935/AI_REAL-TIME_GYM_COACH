/* ==========================================================================
   AI REAL-TIME GYM COACH - LANDING PAGE INTERACTIVE JAVASCRIPT
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initFAQAccordion();
  initWorkoutSimulator();
  initCounterAnimation();
});

/* Navbar Scroll Effect */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

/* FAQ Accordion Toggle */
function initFAQAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    item.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      faqItems.forEach(i => i.classList.remove('open'));
      if (!isOpen) {
        item.classList.add('open');
      }
    });
  });
}

/* Animated Counters on Scroll */
function initCounterAnimation() {
  const counters = document.querySelectorAll('.stat-item .num');
  let animated = false;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !animated) {
        animated = true;
        counters.forEach(counter => {
          const target = +counter.getAttribute('data-target') || 100;
          let count = 0;
          const step = Math.ceil(target / 40);
          const interval = setInterval(() => {
            count += step;
            if (count >= target) {
              counter.innerText = target + (counter.getAttribute('data-suffix') || '');
              clearInterval(interval);
            } else {
              counter.innerText = count + (counter.getAttribute('data-suffix') || '');
            }
          }, 30);
        });
      }
    });
  }, { threshold: 0.5 });

  const statsSection = document.querySelector('.stats-bar');
  if (statsSection) observer.observe(statsSection);
}

/* Interactive Workout Skeleton Pose Simulator */
function initWorkoutSimulator() {
  const canvas = document.getElementById('simCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  // Simulator State
  let currentExercise = 'squat';
  let t = 0; // Animation frame time
  let repCount = 0;
  let stage = 'UP';
  let audioFeedback = "Form tracking active. Begin repetitions.";

  const angleEl = document.getElementById('simAngle');
  const repsEl = document.getElementById('simReps');
  const stageEl = document.getElementById('simStage');
  const statusEl = document.getElementById('simStatus');
  const audioTextEl = document.getElementById('simAudioText');

  // Exercise Buttons
  const exButtons = document.querySelectorAll('.ex-btn');
  exButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      exButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentExercise = btn.getAttribute('data-exercise');
      repCount = 0;
      stage = 'UP';
      if (repsEl) repsEl.innerText = repCount;
      updateAudioFeedback(`Switched to ${currentExercise.toUpperCase()} mode.`);
    });
  });

  function updateAudioFeedback(msg) {
    if (audioTextEl) {
      audioTextEl.innerText = `"${msg}"`;
    }
  }

  function animate() {
    t += 0.04;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2 + 10;
    const scale = Math.min(canvas.width, canvas.height) / 400;

    let head, shoulderL, shoulderR, hipL, hipR, kneeL, kneeR, ankleL, ankleR, elbowL, elbowR, wristL, wristR;
    let computedAngle = 170;

    if (currentExercise === 'squat') {
      // Squat kinematics cycle
      const phase = (Math.sin(t) + 1) / 2; // 0 to 1
      const squatDepth = phase * 75 * scale;
      computedAngle = Math.round(175 - phase * 95);

      if (computedAngle < 90 && stage === 'UP') {
        stage = 'DOWN';
        if (stageEl) stageEl.innerText = stage;
        if (statusEl) {
          statusEl.innerText = "GOOD DEPTH!";
          statusEl.className = "status-pill good";
        }
      } else if (computedAngle > 160 && stage === 'DOWN') {
        stage = 'UP';
        repCount++;
        if (stageEl) stageEl.innerText = stage;
        if (repsEl) repsEl.innerText = repCount;
        if (statusEl) {
          statusEl.innerText = "REP COMPLETE";
          statusEl.className = "status-pill good";
        }
        updateAudioFeedback(`Great depth! Rep ${repCount} completed.`);
      }

      head = { x: cx, y: cy - 120 * scale + squatDepth };
      shoulderL = { x: cx - 35 * scale, y: cy - 80 * scale + squatDepth };
      shoulderR = { x: cx + 35 * scale, y: cy - 80 * scale + squatDepth };
      hipL = { x: cx - 25 * scale, y: cy + 10 * scale + squatDepth };
      hipR = { x: cx + 25 * scale, y: cy + 10 * scale + squatDepth };

      const kneeSpread = phase * 20 * scale;
      kneeL = { x: cx - 40 * scale - kneeSpread, y: cy + 70 * scale + squatDepth * 0.4 };
      kneeR = { x: cx + 40 * scale + kneeSpread, y: cy + 70 * scale + squatDepth * 0.4 };

      ankleL = { x: cx - 35 * scale, y: cy + 130 * scale };
      ankleR = { x: cx + 35 * scale, y: cy + 130 * scale };

      elbowL = { x: cx - 60 * scale, y: cy - 50 * scale + squatDepth };
      elbowR = { x: cx + 60 * scale, y: cy - 50 * scale + squatDepth };
      wristL = { x: cx - 40 * scale, y: cy - 70 * scale + squatDepth };
      wristR = { x: cx + 40 * scale, y: cy - 70 * scale + squatDepth };

    } else if (currentExercise === 'biceps') {
      // Biceps curl kinematics cycle
      const phase = (Math.sin(t) + 1) / 2;
      computedAngle = Math.round(165 - phase * 125);

      if (computedAngle < 40 && stage === 'DOWN') {
        stage = 'UP';
        repCount++;
        if (stageEl) stageEl.innerText = stage;
        if (repsEl) repsEl.innerText = repCount;
        if (statusEl) {
          statusEl.innerText = "FULL FLEXION";
          statusEl.className = "status-pill good";
        }
        updateAudioFeedback(`Squeeze at the top! Rep ${repCount} counted.`);
      } else if (computedAngle > 150 && stage === 'UP') {
        stage = 'DOWN';
        if (stageEl) stageEl.innerText = stage;
      }

      head = { x: cx, y: cy - 120 * scale };
      shoulderL = { x: cx - 35 * scale, y: cy - 80 * scale };
      shoulderR = { x: cx + 35 * scale, y: cy - 80 * scale };
      hipL = { x: cx - 25 * scale, y: cy + 20 * scale };
      hipR = { x: cx + 25 * scale, y: cy + 20 * scale };
      kneeL = { x: cx - 25 * scale, y: cy + 80 * scale };
      kneeR = { x: cx + 25 * scale, y: cy + 80 * scale };
      ankleL = { x: cx - 25 * scale, y: cy + 140 * scale };
      ankleR = { x: cx + 25 * scale, y: cy + 140 * scale };

      elbowL = { x: cx - 40 * scale, y: cy - 20 * scale };
      elbowR = { x: cx + 40 * scale, y: cy - 20 * scale };

      const curlY = cy - 20 * scale - Math.sin(phase * Math.PI) * 55 * scale;
      wristL = { x: cx - 45 * scale, y: curlY };
      wristR = { x: cx + 45 * scale, y: curlY };

    } else {
      // Pushup kinematics
      const phase = (Math.sin(t) + 1) / 2;
      const pushDepth = phase * 40 * scale;
      computedAngle = Math.round(170 - phase * 90);

      if (computedAngle < 90 && stage === 'UP') {
        stage = 'DOWN';
        if (stageEl) stageEl.innerText = stage;
      } else if (computedAngle > 160 && stage === 'DOWN') {
        stage = 'UP';
        repCount++;
        if (stageEl) stageEl.innerText = stage;
        if (repsEl) repsEl.innerText = repCount;
        if (statusEl) {
          statusEl.innerText = "CHEST TO FLOOR";
          statusEl.className = "status-pill good";
        }
        updateAudioFeedback(`Solid pushup form! Rep ${repCount}.`);
      }

      head = { x: cx - 110 * scale, y: cy + 20 * scale + pushDepth };
      shoulderL = { x: cx - 70 * scale, y: cy + 25 * scale + pushDepth };
      shoulderR = { x: cx - 70 * scale, y: cy + 25 * scale + pushDepth };
      hipL = { x: cx, y: cy + 15 * scale };
      hipR = { x: cx, y: cy + 15 * scale };
      kneeL = { x: cx + 60 * scale, y: cy + 15 * scale };
      kneeR = { x: cx + 60 * scale, y: cy + 15 * scale };
      ankleL = { x: cx + 110 * scale, y: cy + 15 * scale };
      ankleR = { x: cx + 110 * scale, y: cy + 15 * scale };

      elbowL = { x: cx - 70 * scale, y: cy + 55 * scale };
      elbowR = { x: cx - 70 * scale, y: cy + 55 * scale };
      wristL = { x: cx - 70 * scale, y: cy + 75 * scale };
      wristR = { x: cx - 70 * scale, y: cy + 75 * scale };
    }

    if (angleEl) angleEl.innerText = computedAngle + '°';

    // Draw Skeleton Bones (Cyan Lines)
    ctx.lineWidth = 4 * scale;
    ctx.strokeStyle = '#00E5FF';
    ctx.shadowBlur = 12;
    ctx.shadowColor = '#00E5FF';

    const connections = [
      [head, shoulderL], [head, shoulderR], [shoulderL, shoulderR],
      [shoulderL, hipL], [shoulderR, hipR], [hipL, hipR],
      [hipL, kneeL], [hipR, kneeR], [kneeL, ankleL], [kneeR, ankleR],
      [shoulderL, elbowL], [elbowL, wristL], [shoulderR, elbowR], [elbowR, wristR]
    ];

    connections.forEach(([p1, p2]) => {
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    });

    // Draw Joint Nodes (Red & White glowing circles)
    const points = [head, shoulderL, shoulderR, hipL, hipR, kneeL, kneeR, ankleL, ankleR, elbowL, elbowR, wristL, wristR];
    points.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 6 * scale, 0, Math.PI * 2);
      ctx.fillStyle = '#FF4B4B';
      ctx.shadowBlur = 10;
      ctx.shadowColor = '#FF4B4B';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(p.x, p.y, 3 * scale, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
    });

    // Angle HUD text on joint
    ctx.shadowBlur = 0;
    ctx.font = `bold ${Math.round(14 * scale)}px Outfit, sans-serif`;
    ctx.fillStyle = '#00E5FF';
    ctx.fillText(`${computedAngle}°`, kneeR.x + 15, kneeR.y);

    requestAnimationFrame(animate);
  }

  animate();
}

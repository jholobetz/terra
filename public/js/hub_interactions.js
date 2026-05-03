/**
 * hub_interactions.js - Client-side interactivity for Platinum Standard Hubs
 */
document.addEventListener('DOMContentLoaded', function() {
    // 1. Formula Expansion Logic
    const list = document.getElementById('equations-list');
    if (list) {
        list.addEventListener('click', function(event) {
            const trigger = event.target.closest('.formula-expand-trigger');
            if (!trigger) return;
            const card = trigger.closest('.platinum-formula-card');
            const body = card.querySelector('.formula-body');
            const icon = trigger.querySelector('.expand-icon');
            if (body) {
                const isHidden = window.getComputedStyle(body).display === 'none';
                if (isHidden) {
                    body.style.display = 'block';
                    card.style.borderColor = 'var(--accent)';
                    icon.innerText = '[ Click to Collapse ]';
                    if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) MathJax.typesetPromise([body]);
                } else {
                    body.style.display = 'none';
                    card.style.borderColor = '#233554';
                    icon.innerText = '[ Click to Expand Depth ]';
                }
            }
        });
    }

    // 2. Global MathJax Fallback Trigger (for complex layouts)
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise();
    }
});

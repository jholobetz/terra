/**
 * 🌌 PHYSICS LAB: Interactive Derivation Accordions
 * 
 * Progressive disclosure handler that manualizes heights for smooth slide/fade animations
 * when opening and closing details/summary derivation accordions.
 */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.derivation-accordion').forEach(el => {
        const summary = el.querySelector('.derivation-summary');
        const content = el.querySelector('.derivation-content');
        if (!summary || !content) return;

        summary.addEventListener('click', (e) => {
            // Prevent default behavior to handle transition manually
            e.preventDefault();
            
            if (el.hasAttribute('open')) {
                // Animate closed
                content.style.overflow = 'hidden';
                const startHeight = content.offsetHeight;
                
                // Set initial height and transition styles
                content.style.height = `${startHeight}px`;
                content.style.opacity = '1';
                content.style.transform = 'translateY(0)';
                
                // Force a browser reflow
                content.offsetHeight;
                
                content.style.transition = 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
                content.style.height = '0px';
                content.style.opacity = '0';
                content.style.transform = 'translateY(-8px)';
                
                // Clean up styles after transition finishes
                setTimeout(() => {
                    el.removeAttribute('open');
                    content.style.height = '';
                    content.style.opacity = '';
                    content.style.transform = '';
                    content.style.transition = '';
                    content.style.overflow = '';
                }, 250);
            } else {
                // Open and animate
                el.setAttribute('open', '');
                const targetHeight = content.offsetHeight;
                
                content.style.overflow = 'hidden';
                content.style.height = '0px';
                content.style.opacity = '0';
                content.style.transform = 'translateY(-8px)';
                
                // Force a browser reflow
                content.offsetHeight;
                
                content.style.transition = 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
                content.style.height = `${targetHeight}px`;
                content.style.opacity = '1';
                content.style.transform = 'translateY(0)';
                
                // Clean up styles after transition finishes
                setTimeout(() => {
                    content.style.height = '';
                    content.style.opacity = '';
                    content.style.transform = '';
                    content.style.transition = '';
                    content.style.overflow = '';
                }, 250);
            }
        });
    });
});

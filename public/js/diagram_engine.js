/**
 * Physics Lab: Abstract Diagram Engine
 * Renders stylized SVGs based on JSON configuration.
 */
class DiagramEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        this.config = JSON.parse(this.container.dataset.config || '{}');
        this.init();
    }

    init() {
        const type = this.config.type || 'abstract';
        const color = this.config.color || '#FFD700';
        const complexity = this.config.complexity || 5;

        let svg = `<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; opacity:0.3;">`;
        
        if (type === 'wave') {
            svg += this.drawWave(color, complexity);
        } else if (type === 'particle') {
            svg += this.drawParticles(color, complexity);
        } else if (type === 'vector') {
            svg += this.drawVectors(color, complexity);
        } else {
            svg += this.drawAbstract(color, complexity);
        }

        svg += `</svg>`;
        this.container.innerHTML = svg;
    }

    drawWave(color, complexity) {
        let paths = '';
        for (let i = 0; i < complexity; i++) {
            const y = 100 + (i * 10) - (complexity * 5);
            paths += `<path d="M 0 ${y} Q 100 ${y - 40}, 200 ${y} T 400 ${y}" stroke="${color}" fill="none" stroke-width="2" />`;
        }
        return paths;
    }

    drawParticles(color, complexity) {
        let dots = '';
        for (let i = 0; i < complexity * 10; i++) {
            const x = Math.random() * 400;
            const y = Math.random() * 200;
            const r = Math.random() * 3 + 1;
            dots += `<circle cx="${x}" cy="${y}" r="${r}" fill="${color}" />`;
        }
        return dots;
    }

    drawVectors(color, complexity) {
        let lines = '';
        for (let x = 0; x < 400; x += 40) {
            for (let y = 0; y < 200; y += 40) {
                lines += `<line x1="${x}" y1="${y}" x2="${x + 20}" y2="${y - 10}" stroke="${color}" stroke-width="2" marker-end="url(#arrowhead)" />`;
            }
        }
        lines += `<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="${color}" /></marker></defs>`;
        return lines;
    }

    drawAbstract(color, complexity) {
        return `<rect x="50" y="50" width="300" height="100" rx="15" stroke="${color}" fill="none" stroke-width="2" stroke-dasharray="10 5" />
                <circle cx="200" cy="100" r="40" stroke="${color}" fill="none" stroke-width="1" />`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DiagramEngine('abstract-diagram');
});

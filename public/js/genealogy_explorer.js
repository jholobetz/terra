/**
 * Concept Derivation Genealogy Explorer (Pillar F)
 * Custom HTML5 Canvas Force-Directed Layout & Lineage Tracker
 */

const NODES = [
    {
        id: "least_action",
        label: "Least Action Principle",
        category: "Axiom",
        equation: "S = \\int_{t_1}^{t_2} L(q, \\dot{q}, t) \\, dt",
        description: "The fundamental axiom of mechanics stating that physical systems trace paths that extremize (usually minimize) the action functional S.",
        color: "#3b82f6" // blue
    },
    {
        id: "euler_lagrange",
        label: "Euler-Lagrange Equations",
        category: "Derivation",
        equation: "\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) - \\frac{\\partial L}{\\partial q_i} = 0",
        description: "Differential equations derived by taking the variational derivative of the action (δS = 0). They govern classical fields and particle trajectories.",
        color: "#8b5cf6" // purple
    },
    {
        id: "hamiltons_principle",
        label: "Hamilton's Principle",
        category: "Derivation",
        equation: "H(p, q) = \\sum p_i \\dot{q}_i - L(q, \\dot{q})",
        description: "Establishes phase-space coordinates by Legendre transforming the Lagrangian velocities into generalized momenta, yielding Hamiltonian energy forms.",
        color: "#8b5cf6" // purple
    },
    {
        id: "hamiltonian_mechanics",
        label: "Hamiltonian Mechanics",
        category: "Core Theory",
        equation: "\\dot{q}_i = \\frac{\\partial H}{\\partial p_i}, \\quad \\dot{p}_i = -\\frac{\\partial H}{\\partial q_i}",
        description: "Reformulates mechanics in 2n-dimensional phase space. Dynamics are described by a set of first-order differential equations representing symplectic flows.",
        color: "#ff4e88" // pink
    },
    {
        id: "hamilton_jacobi",
        label: "Hamilton-Jacobi Equation",
        category: "Derivation",
        equation: "H\\left(q, \\frac{\\partial S}{\\partial q}, t\\right) + \\frac{\\partial S}{\\partial t} = 0",
        description: "Expresses classical mechanics as a wave-like partial differential equation for the action S, serving as the direct mathematical bridge to wave mechanics.",
        color: "#8b5cf6" // purple
    },
    {
        id: "de_broglie",
        label: "De Broglie Relations",
        category: "Axiom",
        equation: "p = \\hbar k, \\quad E = \\hbar \\omega",
        description: "The dual wave-particle postulate relating momentum and energy directly to wave vector k and angular frequency ω.",
        color: "#3b82f6" // blue
    },
    {
        id: "schrodinger",
        label: "Schrödinger Equation",
        category: "Core Theory",
        equation: "i\\hbar \\frac{\\partial}{\\partial t}\\psi = \\left[ -\\frac{\\hbar^2}{2m}\\nabla^2 + V(q) \\right]\\psi",
        description: "The central wave equation of non-relativistic quantum mechanics, derived by substituting De Broglie operators into the Hamilton-Jacobi action wave phase.",
        color: "#ff4e88" // pink
    },
    {
        id: "wkb_approx",
        label: "WKB Approximation",
        category: "Application",
        equation: "\\psi(x) \\approx \\frac{C}{\\sqrt{p(x)}} e^{\\pm \\frac{i}{\\hbar} \\int^x p(x') \\, dx'}",
        description: "A semiclassical approximation method expanding the wavefunction wave phase in powers of ℏ, reducing back to the classical Hamilton-Jacobi action.",
        color: "#10b981" // green
    },
    {
        id: "blochs_theorem",
        label: "Bloch's Theorem",
        category: "Application",
        equation: "\\psi(\\mathbf{r}) = e^{i\\mathbf{k}\\cdot\\mathbf{r}} u_{\\mathbf{k}}(\\mathbf{r})",
        description: "Solves the Schrödinger equation for periodic potentials, proving wavefunctions in crystals consist of plane waves modulated by periodic envelopes.",
        color: "#10b981" // green
    },
    {
        id: "klein_gordon",
        label: "Klein-Gordon Equation",
        category: "Core Theory",
        equation: "\\left( \\square - \\frac{m^2 c^2}{\\hbar^2} \\right)\\psi = 0",
        description: "Relativistic quantum wave equation for spin-0 particles, derived by applying quantum operators to the Einstein energy-momentum relation.",
        color: "#ff4e88" // pink
    },
    {
        id: "dirac_equation",
        label: "Dirac Equation",
        category: "Core Theory",
        equation: "\\left( i\\hbar \\gamma^\\mu \\partial_\\mu - m c \\right)\\psi = 0",
        description: "Linearized relativistic quantum wave equation for spin-1/2 fermions, naturally predicting antimatter and explaining electron spin.",
        color: "#ff4e88" // pink
    },
    {
        id: "classical_newton",
        label: "Newtonian Mechanics",
        category: "Classical Limit",
        equation: "\\mathbf{F} = m\\mathbf{a}",
        description: "The historical vector formulation of dynamics based on forces, serving as the macroscopic limit of quantum expectation values.",
        color: "#10b981" // green
    }
];

const LINKS = [
    { source: "least_action", target: "euler_lagrange" },
    { source: "euler_lagrange", target: "hamiltons_principle" },
    { source: "hamiltons_principle", target: "hamiltonian_mechanics" },
    { source: "hamiltonian_mechanics", target: "hamilton_jacobi" },
    { source: "hamilton_jacobi", target: "schrodinger" },
    { source: "de_broglie", target: "schrodinger" },
    { source: "de_broglie", target: "klein_gordon" },
    { source: "schrodinger", target: "wkb_approx" },
    { source: "schrodinger", target: "blochs_theorem" },
    { source: "schrodinger", target: "classical_newton" },
    { source: "klein_gordon", target: "dirac_equation" }
];

// Active State
let selectedNode = null;
let hoveredNode = null;
let searchQuery = "";

// Canvas details
let canvas, ctx;

// Physics Simulation parameters (Force directed layout)
const springLength = 80;
const springStrength = 0.04;
const repulsionStrength = 650;
const gravityStrength = 0.012;
const friction = 0.88;

// Drag and drop state
let dragNode = null;
let mouseX = 0;
let mouseY = 0;

document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("genealogy-canvas");
    ctx = canvas.getContext("2d");

    // Resize canvas
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initialize node positions randomly near center
    resetPositions();

    // Event listeners
    setupEvents();
    
    // UI Recenter button
    document.getElementById("reset-forces-btn").addEventListener("click", () => {
        resetPositions();
    });

    // Search bar input
    document.getElementById("node-search").addEventListener("input", (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
    });

    // Start loop
    requestAnimationFrame(animationLoop);
});

function resetPositions() {
    if (!canvas) return;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    NODES.forEach(node => {
        node.x = cx + (Math.random() - 0.5) * 160;
        node.y = cy + (Math.random() - 0.5) * 160;
        node.vx = 0;
        node.vy = 0;
        node.r = 22; // default radius
    });
}

function setupEvents() {
    canvas.addEventListener("mousedown", onMouseDown);
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mouseup", onMouseUp);
    canvas.addEventListener("mouseleave", onMouseUp);
}

function onMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;

    // Check if clicked a node
    dragNode = findNodeAt(mouseX, mouseY);
    if (dragNode) {
        selectNode(dragNode);
    } else {
        // click outside resets selection
        selectedNode = null;
        document.getElementById("inspector-content").style.display = "none";
        document.getElementById("inspector-tip").style.display = "block";
    }
}

function onMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;

    if (dragNode) {
        dragNode.x = mouseX;
        dragNode.y = mouseY;
        dragNode.vx = 0;
        dragNode.vy = 0;
    } else {
        // check hover
        hoveredNode = findNodeAt(mouseX, mouseY);
        canvas.style.cursor = hoveredNode ? "pointer" : (dragNode ? "grabbing" : "grab");
    }
}

function onMouseUp() {
    dragNode = null;
    canvas.style.cursor = hoveredNode ? "pointer" : "grab";
}

function findNodeAt(x, y) {
    for (let i = 0; i < NODES.length; i++) {
        const node = NODES[i];
        const dx = node.x - x;
        const dy = node.y - y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist <= node.r) {
            return node;
        }
    }
    return null;
}

// Lineage calculations: find all ancestors and descendants of a node
function getLineage(nodeId) {
    const ancestors = new Set();
    const descendants = new Set();

    // Trace ancestors (DFS backwards)
    function findAncestors(currId) {
        LINKS.forEach(link => {
            if (link.target === currId && !ancestors.has(link.source)) {
                ancestors.add(link.source);
                findAncestors(link.source);
            }
        });
    }

    // Trace descendants (DFS forwards)
    function findDescendants(currId) {
        LINKS.forEach(link => {
            if (link.source === currId && !descendants.has(link.target)) {
                descendants.add(link.target);
                findDescendants(link.target);
            }
        });
    }

    findAncestors(nodeId);
    findDescendants(nodeId);

    return { ancestors: Array.from(ancestors), descendants: Array.from(descendants) };
}

function selectNode(node) {
    selectedNode = node;
    
    // Update left panel
    document.getElementById("inspector-tip").style.display = "none";
    const content = document.getElementById("inspector-content");
    content.style.display = "block";

    document.getElementById("active-node-title").textContent = node.label;
    document.getElementById("active-node-type").textContent = node.category;
    document.getElementById("active-node-desc").textContent = node.description;
    
    // Update badge class color
    const badge = document.getElementById("active-node-type");
    badge.className = "category-badge";
    badge.style.color = node.color;
    badge.style.borderColor = node.color.replace(")", ", 0.35)").replace("#", "rgba("); // approximate alpha
    
    // Renders math identity
    document.getElementById("active-node-math").innerHTML = `\\[ ${node.equation} \\]`;
    if (window.MathJax) {
        MathJax.typesetPromise();
    }

    // Renders Ancestors & Descendants lists
    const lineage = getLineage(node.id);
    
    const ancContainer = document.getElementById("active-node-ancestors");
    ancContainer.innerHTML = "";
    if (lineage.ancestors.length > 0) {
        lineage.ancestors.forEach(ancId => {
            const ancNode = NODES.find(n => n.id === ancId);
            const tag = document.createElement("span");
            tag.className = `node-tag ${getTagClass(ancNode.category)}`;
            tag.textContent = ancNode.label;
            tag.addEventListener("click", () => selectNode(ancNode));
            ancContainer.appendChild(tag);
        });
    } else {
        ancContainer.innerHTML = `<span class="tag-empty">None (First Principle Axiom)</span>`;
    }

    const descContainer = document.getElementById("active-node-descendants");
    descContainer.innerHTML = "";
    if (lineage.descendants.length > 0) {
        lineage.descendants.forEach(descId => {
            const descNode = NODES.find(n => n.id === descId);
            const tag = document.createElement("span");
            tag.className = `node-tag ${getTagClass(descNode.category)}`;
            tag.textContent = descNode.label;
            tag.addEventListener("click", () => selectNode(descNode));
            descContainer.appendChild(tag);
        });
    } else {
        descContainer.innerHTML = `<span class="tag-empty">None (Terminal Application)</span>`;
    }
}

function getTagClass(cat) {
    if (cat === "Axiom") return "tag-axiom";
    if (cat === "Derivation") return "tag-derivation";
    if (cat === "Core Theory") return "tag-theory";
    return "tag-application";
}

// Master Loop
function animationLoop() {
    updateForces();
    renderGraph();
    requestAnimationFrame(animationLoop);
}

// Update node coordinates using force layout vectors
function updateForces() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    // 1. Repulsion force between all nodes (Coulomb repulsion)
    for (let i = 0; i < NODES.length; i++) {
        const n1 = NODES[i];
        for (let j = i + 1; j < NODES.length; j++) {
            const n2 = NODES[j];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx*dx + dy*dy) || 1.0;
            
            if (dist < 280) {
                // F = C / d²
                const force = repulsionStrength / (dist * dist);
                const fx = force * (dx / dist);
                const fy = force * (dy / dist);
                
                // apply opposite forces
                if (n1 !== dragNode) {
                    n1.vx -= fx;
                    n1.vy -= fy;
                }
                if (n2 !== dragNode) {
                    n2.vx += fx;
                    n2.vy += fy;
                }
            }
        }
    }

    // 2. Spring attractive forces along links (Hooke's Law)
    LINKS.forEach(link => {
        const sourceNode = NODES.find(n => n.id === link.source);
        const targetNode = NODES.find(n => n.id === link.target);
        
        const dx = targetNode.x - sourceNode.x;
        const dy = targetNode.y - sourceNode.y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1.0;
        
        // F = -k * (d - d0)
        const displacement = dist - springLength;
        const force = displacement * springStrength;
        const fx = force * (dx / dist);
        const fy = force * (dy / dist);
        
        if (sourceNode !== dragNode) {
            sourceNode.vx += fx;
            sourceNode.vy += fy;
        }
        if (targetNode !== dragNode) {
            targetNode.vx -= fx;
            targetNode.vy -= fy;
        }
    });

    // 3. Central gravity force (pulls toward center to prevent drift)
    NODES.forEach(node => {
        if (node === dragNode) return;
        
        const dx = cx - node.x;
        const dy = cy - node.y;
        
        node.vx += dx * gravityStrength;
        node.vy += dy * gravityStrength;
    });

    // 4. Update coordinates & apply damping friction
    NODES.forEach(node => {
        if (node === dragNode) return;
        
        node.x += node.vx;
        node.y += node.vy;
        
        node.vx *= friction;
        node.vy *= friction;

        // Contain in boundaries
        node.x = Math.max(Math.min(node.x, canvas.width - 20), 20);
        node.y = Math.max(Math.min(node.y, canvas.height - 20), 20);
    });
}

// Draw the nodes and connecting links
function renderGraph() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const lineage = selectedNode ? getLineage(selectedNode.id) : null;

    // Check if node is part of active lineage path
    const isLineageNode = (nodeId) => {
        if (!selectedNode) return true;
        if (selectedNode.id === nodeId) return true;
        if (lineage.ancestors.includes(nodeId)) return true;
        if (lineage.descendants.includes(nodeId)) return true;
        return false;
    };

    const isLineageLink = (src, tgt) => {
        if (!selectedNode) return true;
        
        // Direct link fits if source is selected and target is descendant, or target is selected and source is ancestor
        if (src === selectedNode.id && lineage.descendants.includes(tgt)) return true;
        if (tgt === selectedNode.id && lineage.ancestors.includes(src)) return true;
        
        // Relatives cascade links
        if (lineage.ancestors.includes(src) && lineage.ancestors.includes(tgt)) return true;
        if (lineage.descendants.includes(src) && lineage.descendants.includes(tgt)) return true;

        return false;
    };

    // 1. Draw Links (Derivation Paths)
    LINKS.forEach(link => {
        const src = NODES.find(n => n.id === link.source);
        const tgt = NODES.find(n => n.id === link.target);
        
        const activePath = isLineageLink(link.source, link.target);
        
        ctx.strokeStyle = activePath ? "rgba(234, 179, 8, 0.75)" : "rgba(255,255,255,0.04)";
        ctx.lineWidth = activePath ? 3.0 : 1.2;

        // Draw curved bezier line to show arrow flow clearly
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        
        // Midpoint offset curves
        const midX = (src.x + tgt.x) / 2;
        const midY = (src.y + tgt.y) / 2;
        const offset = 15;
        const dx = tgt.x - src.x;
        const dy = tgt.y - src.y;
        const len = Math.sqrt(dx*dx + dy*dy) || 1.0;
        
        // orthogonal displacement vector
        const ox = -dy / len * offset;
        const oy = dx / len * offset;
        
        const ctrlX = midX + ox;
        const ctrlY = midY + oy;
        
        ctx.quadraticCurveTo(ctrlX, ctrlY, tgt.x, tgt.y);
        ctx.stroke();

        // Draw arrow tip on line midpoint towards target
        // Calculate tangent vector at 3/4 length of curve
        const t = 0.75;
        const tangentX = 2*(1-t)*(ctrlX - src.x) + 2*t*(tgt.x - ctrlX);
        const tangentY = 2*(1-t)*(ctrlY - src.y) + 2*t*(tgt.y - ctrlY);
        const angle = Math.atan2(tangentY, tangentX);
        
        // Position at 3/4 curve
        const ax = (1-t)*(1-t)*src.x + 2*(1-t)*t*ctrlX + t*t*tgt.x;
        const ay = (1-t)*(1-t)*src.y + 2*(1-t)*t*ctrlY + t*t*tgt.y;

        ctx.fillStyle = activePath ? "#ffd700" : "rgba(255,255,255,0.1)";
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(ax - 6 * Math.cos(angle - Math.PI/6), ay - 6 * Math.sin(angle - Math.PI/6));
        ctx.lineTo(ax - 6 * Math.cos(angle + Math.PI/6), ay - 6 * Math.sin(angle + Math.PI/6));
        ctx.closePath();
        ctx.fill();
    });

    // 2. Draw Nodes
    NODES.forEach(node => {
        const activeNode = isLineageNode(node.id);
        const isSelected = selectedNode && selectedNode.id === node.id;
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        const isSearching = searchQuery !== "" && node.label.toLowerCase().includes(searchQuery);

        // Computed Node properties
        node.r = isSelected ? 24 : (isHovered ? 21 : 18);
        
        // Draw glow effect for selected/hovered nodes
        if (isSelected || isHovered || isSearching) {
            ctx.shadowColor = node.color;
            ctx.shadowBlur = isSelected ? 20 : 12;
        }

        // Determine node alpha opacity
        let opacity = 1.0;
        if (selectedNode && !activeNode) {
            opacity = 0.15;
        }
        if (searchQuery !== "" && !isSearching) {
            opacity = 0.15;
        }

        ctx.fillStyle = hexToRgba(node.color, opacity);
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI*2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        // Draw border ring
        ctx.strokeStyle = isSelected ? "#ffffff" : hexToRgba(node.color, opacity + 0.2);
        ctx.lineWidth = isSelected ? 3.0 : 1.5;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI*2);
        ctx.stroke();

        // Draw math mini symbol inside core
        ctx.fillStyle = isSelected ? "#020617" : "#ffffff";
        ctx.font = "bold 10px sans-serif";
        ctx.textAlign = "center";
        
        let initial = node.label.split(" ").map(w => w[0]).join("").substring(0, 2);
        ctx.fillText(initial, node.x, node.y + 3);

        // Draw Label text below node
        ctx.fillStyle = isSelected ? "#ffffff" : `rgba(255,255,255, ${opacity * 0.85})`;
        ctx.font = isSelected ? "bold 11px Space Grotesk, sans-serif" : "10px Space Grotesk, sans-serif";
        ctx.fillText(node.label, node.x, node.y + node.r + 15);
    });

    // 3. Draw hover tooltip overlay
    if (hoveredNode && !dragNode) {
        const textW = ctx.measureText(hoveredNode.label).width;
        
        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
        ctx.strokeStyle = hoveredNode.color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.roundRect(mouseX + 15, mouseY - 30, textW + 30, 26, 4);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.font = "10px Space Grotesk, sans-serif";
        ctx.textAlign = "left";
        ctx.fillText(hoveredNode.label, mouseX + 25, mouseY - 13);
    }
}

// Utility to translate hex color strings to rgba
function hexToRgba(hex, alpha) {
    let r = parseInt(hex.slice(1, 3), 16);
    let g = parseInt(hex.slice(3, 5), 16);
    let b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function resizeCanvas() {
    if (canvas) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
}

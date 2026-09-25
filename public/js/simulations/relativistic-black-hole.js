/**
 * 🪐 Physics Lab: Relativistic Kerr Black Hole Raytracer (relativistic-black-hole.js)
 * 
 * High-performance WebGL2 general relativistic null geodesic raytracer around
 * static (Schwarzschild) and spinning (Kerr) black holes.
 * 
 * Physical Features:
 * - Boyer-Lindquist geometry: Event horizon shadow, Cauchy horizon, ergosphere
 * - Lense-Thirring frame-dragging torque in curved spacetime
 * - Relativistic thin accretion disk with Shakura-Sunyaev / Novikov-Thorne temperature profile
 * - Relativistic Doppler beaming and boosting (I_obs = g^4 * I_emit)
 * - Gravitational redshift from gravitational time dilation
 * - Background celestial starfield gravitational lensing and Einstein rings
 * - Smooth interactive orbit camera with inertia and mouse/touch drag
 * - Real-time mathematical telemetry HUD
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const controls = document.getElementById('controls');

    if (!canvas || !controls) {
        console.error('[RelativisticBlackHole] Required DOM elements not found.');
        return;
    }

    // Inject custom styling
    const style = document.createElement('style');
    style.innerHTML = `
        .rbh-section {
            margin-bottom: 14px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 12px;
            border-radius: 8px;
            backdrop-filter: blur(12px);
        }
        .rbh-section-title {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--accent-default, #38bdf8);
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .rbh-control-group {
            margin-bottom: 10px;
        }
        .rbh-control-group:last-child {
            margin-bottom: 0;
        }
        .rbh-control-group label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            color: #cbd5e1;
            margin-bottom: 5px;
        }
        .rbh-val {
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            color: var(--accent-default, #38bdf8);
            font-weight: 600;
        }
        .rbh-control-group input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 5px;
            background: #1e293b;
            border-radius: 3px;
            outline: none;
            cursor: pointer;
            accent-color: var(--accent-default, #38bdf8);
        }
        .rbh-toggle-row {
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }
        .rbh-btn {
            flex: 1;
            padding: 6px 10px;
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.78rem;
            font-family: inherit;
            transition: all 0.15s ease;
            text-align: center;
        }
        .rbh-btn:hover {
            background: rgba(56, 189, 248, 0.12);
            border-color: rgba(56, 189, 248, 0.35);
            color: #f8fafc;
        }
        .rbh-btn.active {
            background: rgba(56, 189, 248, 0.2);
            border-color: var(--accent-default, #38bdf8);
            color: #ffffff;
            font-weight: 600;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
        }
        .rbh-preset-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-top: 6px;
        }
        .rbh-telemetry {
            background: rgba(2, 6, 23, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 8px;
            padding: 10px 12px;
            font-family: 'Fira Code', monospace;
            font-size: 0.76rem;
            color: #94a3b8;
        }
        .rbh-telemetry-row {
            display: flex;
            justify-content: space-between;
            padding: 3px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }
        .rbh-telemetry-row:last-child {
            border-bottom: none;
        }
        .rbh-telemetry-val {
            color: #f1f5f9;
            font-weight: 600;
        }
        .rbh-hud-overlay {
            position: absolute;
            top: 12px;
            left: 12px;
            pointer-events: none;
            font-family: 'Fira Code', monospace;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.7);
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(8px);
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            gap: 12px;
            z-index: 10;
        }
    `;
    document.head.appendChild(style);

    // Add HUD overlay to canvas container
    const canvasContainer = canvas.parentElement;
    if (canvasContainer) {
        canvasContainer.style.position = 'relative';
        const hud = document.createElement('div');
        hud.className = 'rbh-hud-overlay';
        hud.id = 'rbh-canvas-hud';
        hud.innerHTML = `
            <span>FPS: <strong id="hud-fps" style="color: #38bdf8;">--</strong></span>
            <span>Spin a/M: <strong id="hud-spin" style="color: #64ffda;">0.850</strong></span>
            <span>Drag Canvas to Orbit</span>
        `;
        canvasContainer.appendChild(hud);
    }

    // Controls Template
    controls.innerHTML = `
        <!-- Presets -->
        <div class="rbh-section">
            <div class="rbh-section-title">Physical Scenarios</div>
            <div class="rbh-preset-grid">
                <button class="rbh-btn active" data-preset="gargantua">Interstellar (Gargantua)</button>
                <button class="rbh-btn" data-preset="m87">M87* Shadow (EHT)</button>
                <button class="rbh-btn" data-preset="schwarzschild">Static Schwarzschild</button>
                <button class="rbh-btn" data-preset="extreme">Extreme Kerr (a = 0.998)</button>
                <button class="rbh-btn" data-preset="polar">Polar Jet Axis</button>
                <button class="rbh-btn" data-preset="lensing">Pure Star Lensing</button>
            </div>
        </div>

        <!-- Spacetime Geometry -->
        <div class="rbh-section">
            <div class="rbh-section-title">Kerr Spacetime Metric</div>
            <div class="rbh-control-group">
                <label>Black Hole Spin (a/M): <span id="val-spin" class="rbh-val">0.850</span></label>
                <input type="range" id="param-spin" min="0.0" max="0.998" step="0.005" value="0.850">
            </div>
            <div class="rbh-control-group">
                <label>Black Hole Mass (M): <span id="val-mass" class="rbh-val">1.0</span></label>
                <input type="range" id="param-mass" min="0.5" max="2.0" step="0.1" value="1.0">
            </div>
        </div>

        <!-- Accretion Disk Physics -->
        <div class="rbh-section">
            <div class="rbh-section-title">Accretion Disk & Optics</div>
            <div class="rbh-control-group">
                <label>Disk Radiance / Temp: <span id="val-disk-bright" class="rbh-val">1.4</span></label>
                <input type="range" id="param-disk-bright" min="0.0" max="3.0" step="0.1" value="1.4">
            </div>
            <div class="rbh-control-group">
                <label>Disk Outer Radius: <span id="val-disk-outer" class="rbh-val">14.0 M</span></label>
                <input type="range" id="param-disk-outer" min="7.0" max="24.0" step="0.5" value="14.0">
            </div>
            <div class="rbh-control-group">
                <div class="rbh-toggle-row">
                    <button class="rbh-btn active" id="btn-toggle-doppler">Relativistic Doppler: ON</button>
                    <button class="rbh-btn active" id="btn-toggle-disk">Accretion Disk: ON</button>
                </div>
            </div>
        </div>

        <!-- Camera & Environment -->
        <div class="rbh-section">
            <div class="rbh-section-title">Observer & Environment</div>
            <div class="rbh-control-group">
                <label>Observer Distance: <span id="val-cam-dist" class="rbh-val">16.0 M</span></label>
                <input type="range" id="param-cam-dist" min="5.0" max="35.0" step="0.5" value="16.0">
            </div>
            <div class="rbh-control-group">
                <label>Orbital Inclination (θ): <span id="val-cam-inc" class="rbh-val">76°</span></label>
                <input type="range" id="param-cam-inc" min="2" max="88" step="1" value="76">
            </div>
            <div class="rbh-control-group">
                <div class="rbh-toggle-row">
                    <button class="rbh-btn active" id="btn-toggle-stars">Starfield: ON</button>
                    <button class="rbh-btn" id="btn-reset-cam">Reset View</button>
                    <button class="rbh-btn" id="btn-capture-png">Snapshot</button>
                </div>
            </div>
        </div>

        <!-- Mathematical Telemetry -->
        <div class="rbh-section">
            <div class="rbh-section-title">Relativistic Telemetry (HUD)</div>
            <div class="rbh-telemetry" id="telemetry-box">
                <div class="rbh-telemetry-row">
                    <span>Event Horizon (r+):</span>
                    <span class="rbh-telemetry-val" id="tel-r-plus">1.527 M</span>
                </div>
                <div class="rbh-telemetry-row">
                    <span>Cauchy Horizon (r-):</span>
                    <span class="rbh-telemetry-val" id="tel-r-minus">0.473 M</span>
                </div>
                <div class="rbh-telemetry-row">
                    <span>Ergosphere Max (r_E):</span>
                    <span class="rbh-telemetry-val" id="tel-r-ergo">2.000 M</span>
                </div>
                <div class="rbh-telemetry-row">
                    <span>ISCO Radius (r_isco):</span>
                    <span class="rbh-telemetry-val" id="tel-r-isco">2.784 M</span>
                </div>
                <div class="rbh-telemetry-row">
                    <span>Horizon Ang. Vel (Ω_H):</span>
                    <span class="rbh-telemetry-val" id="tel-omega">0.278 c/M</span>
                </div>
            </div>
        </div>
    `;

    // GLSL Raytracer Fragment Shader (WebGL2 / GLSL 300 es)
    const fragmentShaderSource = `#version 300 es
    precision highp float;

    out vec4 fragColor;

    uniform vec2 u_resolution;
    uniform float u_time;
    uniform vec3 u_cam_pos;
    uniform vec3 u_cam_dir;
    uniform vec3 u_cam_up;
    uniform vec3 u_cam_right;

    // Simulation Physics Uniforms
    uniform float u_spin;          // a / M  (0.0 to 0.998)
    uniform float u_mass;          // M (scale)
    uniform float u_disk_bright;   // Accretion disk radiance scale
    uniform float u_disk_outer;    // Outer disk radius
    uniform float u_isco;          // Innermost stable circular orbit radius
    uniform float u_r_plus;        // Outer event horizon radius
    uniform int u_doppler_enabled; // 1 = on, 0 = off
    uniform int u_disk_enabled;    // 1 = on, 0 = off
    uniform int u_stars_enabled;   // 1 = on, 0 = off

    #define PI 3.14159265359
    #define MAX_STEPS 140
    #define ESCAPE_RADIUS 35.0

    // Procedural pseudo-random hash for background stellar field
    float hash(vec3 p) {
        p = fract(p * 0.3183099 + 0.1);
        p *= 17.0;
        return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
    }

    // Stars background sampling with celestial coordinate projection
    vec3 sampleStarfield(vec3 dir) {
        if (u_stars_enabled == 0) return vec3(0.002, 0.003, 0.008);

        // Normalize direction
        vec3 d = normalize(dir);

        // Cosmic background faint glow / dust lane
        float milkyway = pow(max(0.0, 1.0 - abs(d.y * 1.5 + 0.1 * sin(d.x * 3.0))), 4.0);
        vec3 bg = vec3(0.004, 0.006, 0.015) + vec3(0.02, 0.015, 0.035) * milkyway;

        // Multi-tier procedural stars
        vec3 starCoord = d * 180.0;
        vec3 ip = floor(starCoord);
        vec3 fp = fract(starCoord) - 0.5;

        float rnd = hash(ip);
        if (rnd > 0.975) {
            float dist = length(fp);
            float brightness = smoothstep(0.18, 0.0, dist) * pow((rnd - 0.975) / 0.025, 2.0);
            
            // Star color temperature variation
            vec3 starColor = (rnd > 0.992) ? vec3(0.7, 0.85, 1.0) : // Blue-white
                             (rnd > 0.985) ? vec3(1.0, 0.95, 0.8) : // Solar yellow
                                             vec3(1.0, 0.7, 0.5);   // Red dwarf
            bg += starColor * brightness * 3.5;
        }

        return bg;
    }

    // Blackbody color approximation for accretion disk plasma
    vec3 blackbodyColor(float tempNorm) {
        // Temperature normalized 0.0 to 1.0 (from cool red/orange to hot blue-white)
        float t = clamp(tempNorm, 0.0, 1.0);
        vec3 col;
        if (t < 0.35) {
            col = mix(vec3(0.3, 0.02, 0.0), vec3(1.0, 0.35, 0.05), t / 0.35);
        } else if (t < 0.7) {
            col = mix(vec3(1.0, 0.35, 0.05), vec3(1.0, 0.95, 0.75), (t - 0.35) / 0.35);
        } else {
            col = mix(vec3(1.0, 0.95, 0.75), vec3(0.75, 0.88, 1.3), (t - 0.7) / 0.3);
        }
        return col;
    }

    void main() {
        // Normalized device coordinates (-1.0 to 1.0 with aspect ratio correction)
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;

        // Camera ray setup (Field of View ~ 45 deg)
        float fov = 1.25;
        vec3 rayDir = normalize(u_cam_dir * fov + u_cam_right * uv.x + u_cam_up * uv.y);
        vec3 rayPos = u_cam_pos;

        vec3 accumColor = vec3(0.0);
        float transmittance = 1.0;

        float M = u_mass;
        float a = u_spin;
        float rPlus = u_r_plus;
        float rIsco = u_isco;
        float rOuter = u_disk_outer;

        // Raymarch numerical geodesic integration loop
        for (int i = 0; i < MAX_STEPS; i++) {
            float r = length(rayPos);

            // 1. Plunge check: Has ray crossed the event horizon shadow?
            if (r <= rPlus * 1.01) {
                // Ray trapped in the black hole event horizon
                transmittance = 0.0;
                break;
            }

            // 2. Escape check: Has ray escaped to deep flat spacetime?
            if (r >= ESCAPE_RADIUS) {
                break;
            }

            // Adaptive step size: ultra-fine near photon sphere, larger far away
            float dt = clamp(r * 0.065, 0.02, 0.45);

            // Calculate Boyer-Lindquist / Kerr effective acceleration
            // Gravitational pull towards center (1/r^2 + 1/r^3 relativistic term)
            float r2 = r * r;
            float r3 = r2 * r;
            float r5 = r3 * r2;

            // Angular momentum L = rayPos x rayDir
            vec3 L = cross(rayPos, rayDir);
            float L2 = dot(L, L);

            // Relativistic Schwarzschild/Kerr central acceleration
            vec3 aGrav = - (M / r3 + 1.5 * M * L2 / r5) * rayPos;

            // Kerr frame-dragging (Lense-Thirring) Coriolis-like torque from spin vector (0, a, 0)
            // Spin vector aligned with Y-axis in world space
            vec3 spinVec = vec3(0.0, a * M, 0.0);
            float rho2 = r2 + a * a * (rayPos.y * rayPos.y / r2);
            vec3 aDrag = (2.0 * a * M / (rho2 * rho2)) * cross(cross(rayDir, spinVec), rayPos);

            vec3 totalAccel = aGrav + aDrag;

            // Previous position for plane intersection test
            vec3 prevPos = rayPos;

            // Leapfrog / Verlet numerical stepping
            rayPos += rayDir * dt + 0.5 * totalAccel * dt * dt;
            rayDir = normalize(rayDir + totalAccel * dt);

            // 3. Accretion Disk Interaction (Equatorial Plane crossing y = 0)
            if (u_disk_enabled == 1 && (prevPos.y * rayPos.y <= 0.0)) {
                // Calculate exact plane intersection point
                float tPlane = abs(prevPos.y) / (abs(prevPos.y) + abs(rayPos.y) + 1e-6);
                vec3 hitPos = mix(prevPos, rayPos, tPlane);
                float rHit = length(hitPos.xz);

                // Is hit point within accretion disk bounds?
                if (rHit >= rIsco && rHit <= rOuter) {
                    // Shakura-Sunyaev / Novikov-Thorne normalized temperature profile
                    // T(r) proportional to r^(-3/4) * (1 - sqrt(r_isco / r))^(1/4)
                    float rRatio = rHit / rIsco;
                    float baseTemp = pow(rRatio, -0.75) * pow(max(0.001, 1.0 - sqrt(1.0 / rRatio)), 0.25);

                    // Keplerian orbital velocity in Kerr metric: v_phi = sqrt(M) / (r^(3/2) + a*sqrt(M))
                    float vPhi = sqrt(M) / (pow(rHit, 1.5) + a * sqrt(M));
                    vec3 phiHat = normalize(vec3(-hitPos.z, 0.0, hitPos.x)); // Counter-clockwise rotation

                    // Relativistic Doppler Factor: g = sqrt(1 - 2M/r) / (1 - v . n)
                    float gFactor = 1.0;
                    if (u_doppler_enabled == 1) {
                        float vDotRay = dot(phiHat, -rayDir); // Motion towards observer
                        float gravRedshift = sqrt(max(0.05, 1.0 - 2.0 * M / rHit));
                        gFactor = gravRedshift / max(0.2, 1.0 - vPhi * vDotRay);
                    }

                    // Relativistic Beaming: Specific Intensity scales as g^4
                    float beaming = pow(gFactor, 4.0);

                    // Disk opacity / density profile
                    float edgeFade = smoothstep(rIsco, rIsco + 0.4, rHit) * (1.0 - smoothstep(rOuter - 2.5, rOuter, rHit));
                    float density = edgeFade * 0.42 * (1.0 / (0.8 + 0.2 * rRatio));

                    // Color mapped from temperature and Doppler-shifted
                    vec3 diskCol = blackbodyColor(baseTemp * 1.5 * gFactor);
                    vec3 emission = diskCol * beaming * u_disk_bright * 2.2;

                    // Volumetric optical accumulation
                    accumColor += emission * density * transmittance;
                    transmittance *= max(0.0, 1.0 - density * 2.5);

                    if (transmittance < 0.02) {
                        break;
                    }
                }
            }
        }

        // Add background starfield for escaped rays
        if (transmittance > 0.0) {
            vec3 starfield = sampleStarfield(rayDir);
            accumColor += starfield * transmittance;
        }

        // Tonemapping (Reinhard + ACES curve approximation) and subtle bloom
        vec3 mapped = accumColor / (accumColor + vec3(1.0));
        mapped = pow(mapped, vec3(1.0 / 2.2)); // Gamma correction

        fragColor = vec4(mapped, 1.0);
    }
    `;

    // Initialize WebGL Physics Harness
    let harness = null;
    try {
        harness = new WebGLPhysicsHarness(canvas, {
            contextType: 'webgl2',
            pixelRatio: Math.min(window.devicePixelRatio || 1, 2),
            initialCamera: {
                distance: 16.0,
                azimuth: 0.85,
                elevation: 0.24, // ~14 deg elevation (76 deg inclination)
                target: [0.0, 0.0, 0.0],
                minDistance: 4.5,
                maxDistance: 40.0,
                damping: 0.14
            }
        });

        harness.setShaders(fragmentShaderSource);
    } catch (err) {
        console.error('[RelativisticBlackHole] Failed to initialize WebGL Harness:', err);
        controls.innerHTML = `<div class="rbh-section" style="color: #f43f5e;">
            <strong>WebGL Initialization Error:</strong><br>${err.message}
        </div>`;
        return;
    }

    // Physical State & Parameters
    const state = {
        spin: 0.850,
        mass: 1.0,
        diskBright: 1.4,
        diskOuter: 14.0,
        dopplerEnabled: 1,
        diskEnabled: 1,
        starsEnabled: 1
    };

    // Mathematical Helpers for Kerr Horizons & ISCO
    function computeRelativisticQuantities(M, a) {
        // Event horizons: r_± = M ± sqrt(M^2 - a^2)
        const discriminant = Math.max(0, M * M - a * a);
        const rPlus = M + Math.sqrt(discriminant);
        const rMinus = M - Math.sqrt(discriminant);
        const rErgo = 2.0 * M; // Ergosphere maximum on equator

        // ISCO calculation for prograde Kerr orbits
        const aStar = Math.min(0.998, a / M);
        const z1 = 1.0 + Math.cbrt(1.0 - aStar * aStar) * (Math.cbrt(1.0 + aStar) + Math.cbrt(1.0 - aStar));
        const z2 = Math.sqrt(3.0 * aStar * aStar + z1 * z1);
        const rIsco = M * (3.0 + z2 - Math.sqrt(Math.max(0, (3.0 - z1) * (3.0 + z1 + 2.0 * z2))));

        // Horizon angular velocity Ω_H = a / (2 M r_+)
        const omegaH = a / (2.0 * M * rPlus);

        return { rPlus, rMinus, rErgo, rIsco, omegaH };
    }

    // Telemetry DOM Bindings
    const telRPlus = document.getElementById('tel-r-plus');
    const telRMinus = document.getElementById('tel-r-minus');
    const telRErgo = document.getElementById('tel-r-ergo');
    const telRIsco = document.getElementById('tel-r-isco');
    const telOmega = document.getElementById('tel-omega');
    const hudFps = document.getElementById('hud-fps');
    const hudSpin = document.getElementById('hud-spin');

    function updateTelemetryAndUniforms() {
        const { rPlus, rMinus, rErgo, rIsco, omegaH } = computeRelativisticQuantities(state.mass, state.spin);

        // Update Uniforms
        harness.setUniform('u_spin', '1f', state.spin);
        harness.setUniform('u_mass', '1f', state.mass);
        harness.setUniform('u_disk_bright', '1f', state.diskBright);
        harness.setUniform('u_disk_outer', '1f', state.diskOuter);
        harness.setUniform('u_isco', '1f', rIsco);
        harness.setUniform('u_r_plus', '1f', rPlus);
        harness.setUniform('u_doppler_enabled', '1i', state.dopplerEnabled);
        harness.setUniform('u_disk_enabled', '1i', state.diskEnabled);
        harness.setUniform('u_stars_enabled', '1i', state.starsEnabled);

        // Update DOM Telemetry
        if (telRPlus) telRPlus.textContent = `${rPlus.toFixed(3)} M`;
        if (telRMinus) telRMinus.textContent = `${rMinus.toFixed(3)} M`;
        if (telRErgo) telRErgo.textContent = `${rErgo.toFixed(3)} M`;
        if (telRIsco) telRIsco.textContent = `${rIsco.toFixed(3)} M`;
        if (telOmega) telOmega.textContent = `${omegaH.toFixed(3)} c/M`;
        if (hudSpin) hudSpin.textContent = state.spin.toFixed(3);
    }

    // Sliders & DOM Controls
    const paramSpin = document.getElementById('param-spin');
    const valSpin = document.getElementById('val-spin');
    if (paramSpin) {
        paramSpin.addEventListener('input', (e) => {
            state.spin = parseFloat(e.target.value);
            valSpin.textContent = state.spin.toFixed(3);
            updateTelemetryAndUniforms();
        });
    }

    const paramMass = document.getElementById('param-mass');
    const valMass = document.getElementById('val-mass');
    if (paramMass) {
        paramMass.addEventListener('input', (e) => {
            state.mass = parseFloat(e.target.value);
            valMass.textContent = state.mass.toFixed(1);
            updateTelemetryAndUniforms();
        });
    }

    const paramDiskBright = document.getElementById('param-disk-bright');
    const valDiskBright = document.getElementById('val-disk-bright');
    if (paramDiskBright) {
        paramDiskBright.addEventListener('input', (e) => {
            state.diskBright = parseFloat(e.target.value);
            valDiskBright.textContent = state.diskBright.toFixed(1);
            updateTelemetryAndUniforms();
        });
    }

    const paramDiskOuter = document.getElementById('param-disk-outer');
    const valDiskOuter = document.getElementById('val-disk-outer');
    if (paramDiskOuter) {
        paramDiskOuter.addEventListener('input', (e) => {
            state.diskOuter = parseFloat(e.target.value);
            valDiskOuter.textContent = `${state.diskOuter.toFixed(1)} M`;
            updateTelemetryAndUniforms();
        });
    }

    const paramCamDist = document.getElementById('param-cam-dist');
    const valCamDist = document.getElementById('val-cam-dist');
    if (paramCamDist) {
        paramCamDist.addEventListener('input', (e) => {
            const dist = parseFloat(e.target.value);
            harness.cameraTargetAngles.distance = dist;
            valCamDist.textContent = `${dist.toFixed(1)} M`;
        });
    }

    const paramCamInc = document.getElementById('param-cam-inc');
    const valCamInc = document.getElementById('val-cam-inc');
    if (paramCamInc) {
        paramCamInc.addEventListener('input', (e) => {
            const incDeg = parseFloat(e.target.value);
            // Elevation = 90 - Inclination
            const elevationRad = ((90 - incDeg) * Math.PI) / 180.0;
            harness.cameraTargetAngles.elevation = elevationRad;
            valCamInc.textContent = `${incDeg}°`;
        });
    }

    // Toggle Buttons
    const btnDoppler = document.getElementById('btn-toggle-doppler');
    if (btnDoppler) {
        btnDoppler.addEventListener('click', () => {
            state.dopplerEnabled = state.dopplerEnabled ? 0 : 1;
            btnDoppler.textContent = `Relativistic Doppler: ${state.dopplerEnabled ? 'ON' : 'OFF'}`;
            btnDoppler.classList.toggle('active', !!state.dopplerEnabled);
            updateTelemetryAndUniforms();
        });
    }

    const btnDisk = document.getElementById('btn-toggle-disk');
    if (btnDisk) {
        btnDisk.addEventListener('click', () => {
            state.diskEnabled = state.diskEnabled ? 0 : 1;
            btnDisk.textContent = `Accretion Disk: ${state.diskEnabled ? 'ON' : 'OFF'}`;
            btnDisk.classList.toggle('active', !!state.diskEnabled);
            updateTelemetryAndUniforms();
        });
    }

    const btnStars = document.getElementById('btn-toggle-stars');
    if (btnStars) {
        btnStars.addEventListener('click', () => {
            state.starsEnabled = state.starsEnabled ? 0 : 1;
            btnStars.textContent = `Starfield: ${state.starsEnabled ? 'ON' : 'OFF'}`;
            btnStars.classList.toggle('active', !!state.starsEnabled);
            updateTelemetryAndUniforms();
        });
    }

    const btnResetCam = document.getElementById('btn-reset-cam');
    if (btnResetCam) {
        btnResetCam.addEventListener('click', () => {
            harness.setCameraOrbit(0.85, 0.24, 16.0);
            if (paramCamDist) paramCamDist.value = '16.0';
            if (valCamDist) valCamDist.textContent = '16.0 M';
            if (paramCamInc) paramCamInc.value = '76';
            if (valCamInc) valCamInc.textContent = '76°';
        });
    }

    const btnCapture = document.getElementById('btn-capture-png');
    if (btnCapture) {
        btnCapture.addEventListener('click', () => {
            harness.capturePNG(`relativistic_black_hole_a${state.spin.toFixed(2)}.png`);
        });
    }

    // Preset Handlers
    const presetButtons = document.querySelectorAll('[data-preset]');
    presetButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            presetButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const preset = btn.getAttribute('data-preset');
            switch (preset) {
                case 'gargantua':
                    state.spin = 0.99;
                    state.mass = 1.0;
                    state.diskBright = 1.6;
                    state.diskOuter = 16.0;
                    state.dopplerEnabled = 1;
                    state.diskEnabled = 1;
                    harness.setCameraOrbit(0.85, 0.15, 14.5); // ~81 deg inclination
                    break;
                case 'm87':
                    state.spin = 0.35;
                    state.mass = 1.2;
                    state.diskBright = 1.2;
                    state.diskOuter = 10.0;
                    state.dopplerEnabled = 1;
                    state.diskEnabled = 1;
                    harness.setCameraOrbit(0.3, 1.27, 18.0); // ~17 deg inclination
                    break;
                case 'schwarzschild':
                    state.spin = 0.0;
                    state.mass = 1.0;
                    state.diskBright = 1.3;
                    state.diskOuter = 18.0;
                    state.dopplerEnabled = 1;
                    state.diskEnabled = 1;
                    harness.setCameraOrbit(0.6, 0.35, 17.0);
                    break;
                case 'extreme':
                    state.spin = 0.998;
                    state.mass = 1.0;
                    state.diskBright = 1.8;
                    state.diskOuter = 14.0;
                    state.dopplerEnabled = 1;
                    state.diskEnabled = 1;
                    harness.setCameraOrbit(1.1, 0.2, 13.0);
                    break;
                case 'polar':
                    state.spin = 0.92;
                    state.mass = 1.0;
                    state.diskBright = 1.5;
                    state.diskOuter = 15.0;
                    state.dopplerEnabled = 1;
                    state.diskEnabled = 1;
                    harness.setCameraOrbit(0.0, 1.48, 16.0); // ~5 deg from pole
                    break;
                case 'lensing':
                    state.spin = 0.7;
                    state.mass = 1.4;
                    state.diskBright = 0.0;
                    state.diskEnabled = 0;
                    state.starsEnabled = 1;
                    harness.setCameraOrbit(0.0, 0.0, 15.0);
                    break;
            }

            // Sync slider inputs
            if (paramSpin) paramSpin.value = state.spin;
            if (valSpin) valSpin.textContent = state.spin.toFixed(3);
            if (paramMass) paramMass.value = state.mass;
            if (valMass) valMass.textContent = state.mass.toFixed(1);
            if (paramDiskBright) paramDiskBright.value = state.diskBright;
            if (valDiskBright) valDiskBright.textContent = state.diskBright.toFixed(1);
            if (btnDisk) {
                btnDisk.textContent = `Accretion Disk: ${state.diskEnabled ? 'ON' : 'OFF'}`;
                btnDisk.classList.toggle('active', !!state.diskEnabled);
            }

            updateTelemetryAndUniforms();
        });
    });

    // Frame Hook for Telemetry Sync (FPS and Camera Readout)
    harness.onFrameHook = () => {
        if (hudFps) {
            hudFps.textContent = harness.fps;
        }

        // Sync slider display with interactive drag rotation
        if (paramCamDist && Math.abs(parseFloat(paramCamDist.value) - harness.camera.distance) > 0.1) {
            const d = harness.camera.distance;
            paramCamDist.value = d.toFixed(1);
            if (valCamDist) valCamDist.textContent = `${d.toFixed(1)} M`;
        }

        if (paramCamInc) {
            const incDeg = Math.round(90 - (harness.camera.elevation * 180.0) / Math.PI);
            paramCamInc.value = incDeg;
            if (valCamInc) valCamInc.textContent = `${incDeg}°`;
        }
    };

    // Initial sync and start loop
    updateTelemetryAndUniforms();
    harness.start();

    // Cleanup on window unload
    window.addEventListener('beforeunload', () => {
        harness.destroy();
    });
});

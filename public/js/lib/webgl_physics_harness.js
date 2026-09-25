/**
 * 🪐 Physics Lab: WebGL Physics Harness (webgl_physics_harness.js)
 * 
 * High-performance, zero-dependency WebGL2 shader harness for GPU-accelerated
 * physical simulations, relativistic raymarching, and PDE field solvers.
 * 
 * Features:
 * - WebGL2 context initialization with WebGL1 fallback
 * - Full-screen quad geometry and program compilation with formatted error logs
 * - Automatic standard uniform bindings (resolution, time, delta, frame, mouse, camera)
 * - Built-in spherical orbit camera with smooth inertia damping and touch support
 * - Dynamic custom uniform registration and binding pipeline
 * - Double-buffered ping-pong FBOs for multi-pass iterative PDE field equations
 * - HiDPI Retina scaling with dynamic quality/downsampling controls
 * - Built-in telemetry metrics (FPS, GPU step count, resolution)
 * - Screenshot capture utility
 */

(function (global) {
    'use strict';

    class WebGLPhysicsHarness {
        /**
         * @param {HTMLCanvasElement} canvas
         * @param {Object} options
         */
        constructor(canvas, options = {}) {
            if (!canvas) {
                throw new Error('[WebGLPhysicsHarness] A valid HTMLCanvasElement must be provided.');
            }

            this.canvas = canvas;
            this.options = Object.assign({
                contextType: 'webgl2',
                powerPreference: 'high-performance',
                antialias: true,
                alpha: false,
                depth: false,
                preserveDrawingBuffer: true,
                pixelRatio: Math.min(window.devicePixelRatio || 1, 2),
                cameraEnabled: true,
                initialCamera: {
                    distance: 18.0,
                    azimuth: 0.85,
                    elevation: 0.28,
                    target: [0.0, 0.0, 0.0],
                    minDistance: 3.0,
                    maxDistance: 60.0,
                    minElevation: -Math.PI / 2 + 0.05,
                    maxElevation: Math.PI / 2 - 0.05,
                    sensitivity: 0.005,
                    zoomSensitivity: 0.05,
                    damping: 0.12
                }
            }, options);

            this.gl = this._initContext();
            this.isWebGL2 = (typeof WebGL2RenderingContext !== 'undefined' && this.gl instanceof WebGL2RenderingContext);

            // Quad buffer
            this.quadBuffer = this._initQuadBuffer();

            // Active Shader Program & Uniform locations
            this.program = null;
            this.uniformLocations = new Map();
            this.customUniforms = new Map();

            // Timing & Loop
            this.isRunning = false;
            this.animationFrameId = null;
            this.startTime = performance.now();
            this.currentTime = 0;
            this.lastFrameTime = performance.now();
            this.deltaTime = 0;
            this.frameCount = 0;

            // Telemetry & FPS
            this.fps = 60;
            this._fpsHistory = [];
            this._lastFpsUpdate = performance.now();

            // Camera System
            this.camera = Object.assign({}, this.options.initialCamera);
            this.cameraTargetAngles = {
                azimuth: this.camera.azimuth,
                elevation: this.camera.elevation,
                distance: this.camera.distance
            };
            this.cameraVectors = {
                pos: [0, 0, 0],
                dir: [0, 0, -1],
                up: [0, 1, 0],
                right: [1, 0, 0]
            };

            // Mouse interaction state
            this.mouseState = {
                x: 0,
                y: 0,
                clickX: 0,
                clickY: 0,
                isDown: false,
                prevX: 0,
                prevY: 0
            };

            // Ping-pong framebuffers
            this.pingPongFBOs = null;

            // Hooks
            this.onFrameHook = null;
            this.onResizeHook = null;

            // Bind listeners & observers
            this._bindEvents();
            this._setupResizeObserver();
            this.updateCameraVectors();
            this.resize();
        }

        // =========================================================================
        // Context & Geometry Initialization
        // =========================================================================

        _initContext() {
            const contextAttributes = {
                powerPreference: this.options.powerPreference,
                antialias: this.options.antialias,
                alpha: this.options.alpha,
                depth: this.options.depth,
                preserveDrawingBuffer: this.options.preserveDrawingBuffer
            };

            let gl = null;
            if (this.options.contextType === 'webgl2') {
                gl = this.canvas.getContext('webgl2', contextAttributes);
            }
            if (!gl) {
                console.warn('[WebGLPhysicsHarness] WebGL2 not available, falling back to WebGL1.');
                gl = this.canvas.getContext('webgl', contextAttributes) || 
                     this.canvas.getContext('experimental-webgl', contextAttributes);
            }

            if (!gl) {
                throw new Error('[WebGLPhysicsHarness] WebGL is not supported by this browser or GPU.');
            }

            return gl;
        }

        _initQuadBuffer() {
            const gl = this.gl;
            const positionBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);

            // Two triangles covering full clip-space coordinates [-1, 1]
            const positions = new Float32Array([
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                -1.0,  1.0,
                 1.0, -1.0,
                 1.0,  1.0
            ]);

            gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);
            return positionBuffer;
        }

        // =========================================================================
        // Shader Compilation & Linking
        // =========================================================================

        /**
         * Compiles and links a full screen fragment shader program.
         * @param {string} fragmentSource GLSL fragment shader source code.
         * @param {string} [vertexSource] Optional custom vertex shader.
         * @returns {WebGLProgram}
         */
        setShaders(fragmentSource, vertexSource = null) {
            const gl = this.gl;

            // Default Quad Vertex Shader
            if (!vertexSource) {
                if (this.isWebGL2) {
                    vertexSource = `#version 300 es
                    in vec2 a_position;
                    out vec2 v_uv;
                    void main() {
                        v_uv = (a_position + 1.0) * 0.5;
                        gl_Position = vec4(a_position, 0.0, 1.0);
                    }`;
                } else {
                    vertexSource = `
                    attribute vec2 a_position;
                    varying vec2 v_uv;
                    void main() {
                        v_uv = (a_position + 1.0) * 0.5;
                        gl_Position = vec4(a_position, 0.0, 1.0);
                    }`;
                }
            }

            const vertexShader = this._compileShader(gl.VERTEX_SHADER, vertexSource);
            const fragmentShader = this._compileShader(gl.FRAGMENT_SHADER, fragmentSource);

            const program = gl.createProgram();
            gl.attachShader(program, vertexShader);
            gl.attachShader(program, fragmentShader);
            gl.linkProgram(program);

            if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
                const info = gl.getProgramInfoLog(program);
                gl.deleteProgram(program);
                throw new Error(`[WebGLPhysicsHarness] Program Link Failure:\n${info}`);
            }

            // Cleanup attached shaders once linked
            gl.deleteShader(vertexShader);
            gl.deleteShader(fragmentShader);

            this.program = program;
            this.uniformLocations.clear();
            gl.useProgram(this.program);

            // Bind Quad Position Attribute
            const positionLocation = gl.getAttribLocation(program, 'a_position');
            if (positionLocation !== -1) {
                gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
                gl.enableVertexAttribArray(positionLocation);
                gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
            }

            return program;
        }

        _compileShader(type, source) {
            const gl = this.gl;
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);

            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                const info = gl.getShaderInfoLog(shader);
                const typeName = type === gl.VERTEX_SHADER ? 'VERTEX' : 'FRAGMENT';
                this._logFormattedShaderError(typeName, info, source);
                gl.deleteShader(shader);
                throw new Error(`[WebGLPhysicsHarness] ${typeName} Shader Compile Error:\n${info}`);
            }

            return shader;
        }

        _logFormattedShaderError(stage, log, source) {
            console.error(`=== [WebGLPhysicsHarness] ${stage} SHADER COMPILE ERROR ===`);
            console.error(log);
            const lines = source.split('\n');
            const match = log.match(/ERROR:\s*\d+:(\d+):/i);
            const errLine = match ? parseInt(match[1], 10) : -1;

            if (errLine > 0) {
                const start = Math.max(0, errLine - 4);
                const end = Math.min(lines.length, errLine + 3);
                console.groupCollapsed(`Context around line ${errLine}:`);
                for (let i = start; i < end; i++) {
                    const prefix = (i + 1 === errLine) ? '>> ' : '   ';
                    console.log(`${prefix}${i + 1}: ${lines[i]}`);
                }
                console.groupEnd();
            }
        }

        // =========================================================================
        // Uniform Pipeline
        // =========================================================================

        /**
         * Caches uniform locations to eliminate runtime string lookups.
         * @param {string} name
         * @returns {WebGLUniformLocation|null}
         */
        getUniformLocation(name) {
            if (!this.program) return null;
            if (!this.uniformLocations.has(name)) {
                const loc = this.gl.getUniformLocation(this.program, name);
                this.uniformLocations.set(name, loc);
            }
            return this.uniformLocations.get(name);
        }

        /**
         * Sets a custom uniform with type checking and cached locations.
         * @param {string} name Uniform variable name in GLSL.
         * @param {string} type '1f'|'2f'|'3f'|'4f'|'1i'|'1iv'|'2fv'|'3fv'|'4fv'|'matrix3fv'|'matrix4fv'
         * @param {number|Array|Float32Array} value
         */
        setUniform(name, type, value) {
            this.customUniforms.set(name, { type, value });
            if (this.program) {
                this._applyUniform(name, type, value);
            }
        }

        _applyUniform(name, type, value) {
            const loc = this.getUniformLocation(name);
            if (!loc) return;

            const gl = this.gl;
            switch (type) {
                case '1f': gl.uniform1f(loc, value); break;
                case '2f': gl.uniform2f(loc, value[0], value[1]); break;
                case '3f': gl.uniform3f(loc, value[0], value[1], value[2]); break;
                case '4f': gl.uniform4f(loc, value[0], value[1], value[2], value[3]); break;
                case '1i': gl.uniform1i(loc, value); break;
                case '1iv': gl.uniform1iv(loc, value); break;
                case '2fv': gl.uniform2fv(loc, value); break;
                case '3fv': gl.uniform3fv(loc, value); break;
                case '4fv': gl.uniform4fv(loc, value); break;
                case 'matrix3fv': gl.uniformMatrix3fv(loc, false, value); break;
                case 'matrix4fv': gl.uniformMatrix4fv(loc, false, value); break;
                default:
                    console.warn(`[WebGLPhysicsHarness] Unknown uniform type: ${type}`);
            }
        }

        _applyStandardUniforms() {
            const gl = this.gl;
            gl.useProgram(this.program);

            // 1. Resolution
            const resLoc = this.getUniformLocation('u_resolution');
            if (resLoc) {
                gl.uniform2f(resLoc, this.canvas.width, this.canvas.height);
            }

            // 2. Time & Frames
            const timeLoc = this.getUniformLocation('u_time');
            if (timeLoc) {
                gl.uniform1f(timeLoc, this.currentTime);
            }
            const dtLoc = this.getUniformLocation('u_delta_time');
            if (dtLoc) {
                gl.uniform1f(dtLoc, this.deltaTime);
            }
            const frameLoc = this.getUniformLocation('u_frame');
            if (frameLoc) {
                gl.uniform1i(frameLoc, this.frameCount);
            }

            // 3. Mouse State
            const mouseLoc = this.getUniformLocation('u_mouse');
            if (mouseLoc) {
                gl.uniform4f(
                    mouseLoc,
                    this.mouseState.x,
                    this.mouseState.y,
                    this.mouseState.clickX,
                    this.mouseState.clickY
                );
            }

            // 4. Camera System
            const camPosLoc = this.getUniformLocation('u_cam_pos');
            if (camPosLoc) {
                gl.uniform3fv(camPosLoc, this.cameraVectors.pos);
            }
            const camDirLoc = this.getUniformLocation('u_cam_dir');
            if (camDirLoc) {
                gl.uniform3fv(camDirLoc, this.cameraVectors.dir);
            }
            const camUpLoc = this.getUniformLocation('u_cam_up');
            if (camUpLoc) {
                gl.uniform3fv(camUpLoc, this.cameraVectors.up);
            }
            const camRightLoc = this.getUniformLocation('u_cam_right');
            if (camRightLoc) {
                gl.uniform3fv(camRightLoc, this.cameraVectors.right);
            }

            // 5. Custom Registered Uniforms
            this.customUniforms.forEach((spec, name) => {
                this._applyUniform(name, spec.type, spec.value);
            });
        }

        // =========================================================================
        // Orbit Camera Mathematics
        // =========================================================================

        updateCameraVectors() {
            // Apply smooth inertia damping toward target angles
            const d = this.camera.damping;
            this.camera.azimuth += (this.cameraTargetAngles.azimuth - this.camera.azimuth) * d;
            this.camera.elevation += (this.cameraTargetAngles.elevation - this.camera.elevation) * d;
            this.camera.distance += (this.cameraTargetAngles.distance - this.camera.distance) * d;

            const az = this.camera.azimuth;
            const el = this.camera.elevation;
            const dist = this.camera.distance;
            const tgt = this.camera.target;

            // Cartesian coordinates from spherical (Y-up)
            const cx = tgt[0] + dist * Math.cos(el) * Math.sin(az);
            const cy = tgt[1] + dist * Math.sin(el);
            const cz = tgt[2] + dist * Math.cos(el) * Math.cos(az);

            this.cameraVectors.pos[0] = cx;
            this.cameraVectors.pos[1] = cy;
            this.cameraVectors.pos[2] = cz;

            // Direction vector pointing from camera to target
            let dx = tgt[0] - cx;
            let dy = tgt[1] - cy;
            let dz = tgt[2] - cz;
            const dirLen = Math.hypot(dx, dy, dz) || 1.0;
            dx /= dirLen;
            dy /= dirLen;
            dz /= dirLen;

            this.cameraVectors.dir[0] = dx;
            this.cameraVectors.dir[1] = dy;
            this.cameraVectors.dir[2] = dz;

            // World Up: (0, 1, 0)
            // Camera Right = Normalize(Cross(Dir, WorldUp))
            let rx = dz; // dx * 0 - dz * 1
            let ry = 0;
            let rz = -dx; // dx * 1 - 0
            const rightLen = Math.hypot(rx, rz) || 1.0;
            rx /= rightLen;
            rz /= rightLen;

            this.cameraVectors.right[0] = rx;
            this.cameraVectors.right[1] = ry;
            this.cameraVectors.right[2] = rz;

            // Camera Up = Normalize(Cross(Right, Dir))
            let ux = ry * dz - rz * dy;
            let uy = rz * dx - rx * dz;
            let uz = rx * dy - ry * dx;
            const upLen = Math.hypot(ux, uy, uz) || 1.0;
            ux /= upLen;
            uy /= upLen;
            uz /= upLen;

            this.cameraVectors.up[0] = ux;
            this.cameraVectors.up[1] = uy;
            this.cameraVectors.up[2] = uz;
        }

        setCameraOrbit(azimuth, elevation, distance = null) {
            this.cameraTargetAngles.azimuth = azimuth;
            this.cameraTargetAngles.elevation = Math.max(
                this.camera.minElevation,
                Math.min(this.camera.maxElevation, elevation)
            );
            if (distance !== null) {
                this.cameraTargetAngles.distance = Math.max(
                    this.camera.minDistance,
                    Math.min(this.camera.maxDistance, distance)
                );
            }
        }

        // =========================================================================
        // Event Listeners & Interaction
        // =========================================================================

        _bindEvents() {
            const canvas = this.canvas;

            const onPointerDown = (clientX, clientY) => {
                const rect = canvas.getBoundingClientRect();
                const x = clientX - rect.left;
                const y = rect.height - (clientY - rect.top); // GL coordinates (bottom-left origin)

                this.mouseState.isDown = true;
                this.mouseState.x = x;
                this.mouseState.y = y;
                this.mouseState.clickX = x;
                this.mouseState.clickY = y;
                this.mouseState.prevX = clientX;
                this.mouseState.prevY = clientY;
            };

            const onPointerMove = (clientX, clientY) => {
                const rect = canvas.getBoundingClientRect();
                const x = clientX - rect.left;
                const y = rect.height - (clientY - rect.top);

                this.mouseState.x = x;
                this.mouseState.y = y;

                if (this.mouseState.isDown && this.options.cameraEnabled) {
                    const dx = clientX - this.mouseState.prevX;
                    const dy = clientY - this.mouseState.prevY;
                    this.mouseState.prevX = clientX;
                    this.mouseState.prevY = clientY;

                    // Update camera spherical targets
                    this.cameraTargetAngles.azimuth -= dx * this.camera.sensitivity;
                    this.cameraTargetAngles.elevation = Math.max(
                        this.camera.minElevation,
                        Math.min(this.camera.maxElevation, this.cameraTargetAngles.elevation + dy * this.camera.sensitivity)
                    );
                }
            };

            const onPointerUp = () => {
                this.mouseState.isDown = false;
                this.mouseState.clickX = -Math.abs(this.mouseState.clickX);
                this.mouseState.clickY = -Math.abs(this.mouseState.clickY);
            };

            // Mouse Events
            canvas.addEventListener('mousedown', (e) => {
                e.preventDefault();
                onPointerDown(e.clientX, e.clientY);
            });

            window.addEventListener('mousemove', (e) => {
                onPointerMove(e.clientX, e.clientY);
            });

            window.addEventListener('mouseup', () => {
                if (this.mouseState.isDown) {
                    onPointerUp();
                }
            });

            // Wheel / Zoom Event
            canvas.addEventListener('wheel', (e) => {
                e.preventDefault();
                const zoomFactor = e.deltaY * 0.01 * this.camera.zoomSensitivity;
                this.cameraTargetAngles.distance = Math.max(
                    this.camera.minDistance,
                    Math.min(this.camera.maxDistance, this.cameraTargetAngles.distance * (1 + zoomFactor))
                );
            }, { passive: false });

            // Touch Events (Mobile / Tablet support)
            let touchDistanceStart = 0;
            canvas.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    onPointerDown(e.touches[0].clientX, e.touches[0].clientY);
                } else if (e.touches.length === 2) {
                    const dx = e.touches[0].clientX - e.touches[1].clientX;
                    const dy = e.touches[0].clientY - e.touches[1].clientY;
                    touchDistanceStart = Math.hypot(dx, dy);
                }
            }, { passive: true });

            canvas.addEventListener('touchmove', (e) => {
                if (e.touches.length === 1) {
                    onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
                } else if (e.touches.length === 2 && touchDistanceStart > 0) {
                    const dx = e.touches[0].clientX - e.touches[1].clientX;
                    const dy = e.touches[0].clientY - e.touches[1].clientY;
                    const currentDist = Math.hypot(dx, dy);
                    const ratio = touchDistanceStart / currentDist;
                    touchDistanceStart = currentDist;
                    this.cameraTargetAngles.distance = Math.max(
                        this.camera.minDistance,
                        Math.min(this.camera.maxDistance, this.cameraTargetAngles.distance * ratio)
                    );
                }
            }, { passive: true });

            canvas.addEventListener('touchend', (e) => {
                if (e.touches.length === 0) {
                    onPointerUp();
                    touchDistanceStart = 0;
                }
            });
        }

        _setupResizeObserver() {
            if (typeof ResizeObserver !== 'undefined') {
                this.resizeObserver = new ResizeObserver(() => {
                    this.resize();
                });
                this.resizeObserver.observe(this.canvas.parentElement || this.canvas);
            } else {
                window.addEventListener('resize', () => this.resize());
            }
        }

        resize(targetPixelRatio = null) {
            if (targetPixelRatio) {
                this.options.pixelRatio = targetPixelRatio;
            }

            const rect = this.canvas.getBoundingClientRect();
            const dpr = this.options.pixelRatio;
            const displayWidth = Math.max(1, Math.round(rect.width * dpr));
            const displayHeight = Math.max(1, Math.round(rect.height * dpr));

            if (this.canvas.width !== displayWidth || this.canvas.height !== displayHeight) {
                this.canvas.width = displayWidth;
                this.canvas.height = displayHeight;
                this.gl.viewport(0, 0, displayWidth, displayHeight);

                if (this.onResizeHook) {
                    this.onResizeHook(displayWidth, displayHeight);
                }
            }
        }

        // =========================================================================
        // Render Loop & Animation Lifecycle
        // =========================================================================

        start() {
            if (this.isRunning) return;
            this.isRunning = true;
            this.lastFrameTime = performance.now();

            const loop = (now) => {
                if (!this.isRunning) return;

                this.deltaTime = Math.min((now - this.lastFrameTime) / 1000.0, 0.1); // clamp to 100ms max
                this.lastFrameTime = now;
                this.currentTime = (now - this.startTime) / 1000.0;
                this.frameCount++;

                // Update FPS calculation
                this._updateFps(now);

                // Update Camera
                if (this.options.cameraEnabled) {
                    this.updateCameraVectors();
                }

                // Render single frame
                this.render();

                this.animationFrameId = requestAnimationFrame(loop);
            };

            this.animationFrameId = requestAnimationFrame(loop);
        }

        pause() {
            this.isRunning = false;
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
                this.animationFrameId = null;
            }
        }

        togglePlayPause() {
            if (this.isRunning) {
                this.pause();
            } else {
                this.start();
            }
            return this.isRunning;
        }

        resetTime() {
            this.startTime = performance.now();
            this.currentTime = 0;
            this.frameCount = 0;
        }

        _updateFps(now) {
            this._fpsHistory.push(this.deltaTime > 0 ? 1.0 / this.deltaTime : 60);
            if (this._fpsHistory.length > 30) {
                this._fpsHistory.shift();
            }

            if (now - this._lastFpsUpdate >= 300) {
                const sum = this._fpsHistory.reduce((a, b) => a + b, 0);
                this.fps = Math.round(sum / this._fpsHistory.length);
                this._lastFpsUpdate = now;
            }
        }

        render() {
            if (!this.program) return;
            const gl = this.gl;

            if (this.onFrameHook) {
                this.onFrameHook(this.deltaTime, this.currentTime);
            }

            this._applyStandardUniforms();
            gl.drawArrays(gl.TRIANGLES, 0, 6);
        }

        // =========================================================================
        // Double-Buffered Ping-Pong FBO Pipeline (For Multi-Pass PDEs)
        // =========================================================================

        /**
         * Creates a pair of textures and framebuffers for iterative numerical field solving.
         * @param {number} width
         * @param {number} height
         */
        createPingPongFBO(width, height) {
            const gl = this.gl;
            const isWebGL2 = this.isWebGL2;

            // Select 32-bit floating point format if available
            let internalFormat = gl.RGBA;
            let format = gl.RGBA;
            let type = gl.UNSIGNED_BYTE;

            if (isWebGL2) {
                const ext = gl.getExtension('EXT_color_buffer_float');
                if (ext) {
                    internalFormat = gl.RGBA32F;
                    type = gl.FLOAT;
                }
            } else {
                const ext = gl.getExtension('OES_texture_float');
                if (ext) {
                    type = gl.FLOAT;
                }
            }

            const createFbo = () => {
                const texture = gl.createTexture();
                gl.bindTexture(gl.TEXTURE_2D, texture);
                gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, width, height, 0, format, type, null);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

                const fbo = gl.createFramebuffer();
                gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
                gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);

                return { fbo, texture, width, height };
            };

            this.pingPongFBOs = {
                read: createFbo(),
                write: createFbo()
            };

            gl.bindFramebuffer(gl.FRAMEBUFFER, null);
            return this.pingPongFBOs;
        }

        swapPingPong() {
            if (!this.pingPongFBOs) return;
            const tmp = this.pingPongFBOs.read;
            this.pingPongFBOs.read = this.pingPongFBOs.write;
            this.pingPongFBOs.write = tmp;
        }

        // =========================================================================
        // Utilities & Screen Capture
        // =========================================================================

        capturePNG(filename = 'simulation_snapshot.png') {
            this.render();
            const dataUrl = this.canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = filename;
            link.href = dataUrl;
            link.click();
        }

        destroy() {
            this.pause();
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
            }
            if (this.quadBuffer) {
                this.gl.deleteBuffer(this.quadBuffer);
            }
            if (this.program) {
                this.gl.deleteProgram(this.program);
            }
            if (this.pingPongFBOs) {
                this.gl.deleteTexture(this.pingPongFBOs.read.texture);
                this.gl.deleteTexture(this.pingPongFBOs.write.texture);
                this.gl.deleteFramebuffer(this.pingPongFBOs.read.fbo);
                this.gl.deleteFramebuffer(this.pingPongFBOs.write.fbo);
            }
        }
    }

    // Export globally for browser scripts and module bundlers
    global.WebGLPhysicsHarness = WebGLPhysicsHarness;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = WebGLPhysicsHarness;
    }
})(typeof window !== 'undefined' ? window : globalThis);

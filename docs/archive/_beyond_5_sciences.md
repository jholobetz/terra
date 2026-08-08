# Project Terra: Supplemental Sciences Architecture & Expansion Ideas
**Date**: August 5, 2026  
**File**: `docs/_beyond_5_sciences.md`  
**Purpose**: Conceptual design document outlining supplemental quantitative science fields beyond the core 5 departments, detailing mathematical models and interactive sandboxes.

---

## 🏛️ Overview & Expansion Philosophy

While Project Terra's core infrastructure is anchored around the **5 Primary Sciences** (*Physics, Chemistry, Biology, Earth Sciences, Mathematics*), the platform's underlying symbolic engine (LaTeX AST parser, FlightPHP MVC, JSON shards, and DAG Knowledge Graph) can seamlessly scale to encompass additional quantitative and empirical disciplines.

This document details 5 supplemental departments that could be added in future expansion phases.

---

## 🌌 1. Department of Astrophysics & Cosmology (`/astronomy`)
*Focus: Celestial Mechanics, Stellar Evolution, Relativistic Astrophysics, & Observational Cosmology.*

### Foundational Equations & Models:
- **Orbital Dynamics**: Kepler's 3rd Law, N-body gravitational interactions, Lagrange points ($L_1$ through $L_5$).
- **Stellar Interiors**: Lane-Emden equation for polytropes, Eddington luminosity limit, Saha ionization equilibrium.
- **Cosmology**: Friedmann-Lemaître-Robertson-Walker (FLRW) metric, Hubble-Lemaître Law ($v = H_0 d$), Cosmic Microwave Background power spectrum.

### 🧰 Interactive Sandboxes:
1. **🚀 N-Body Gravity Simulator**: Real-time gravitational orbital sandbox (slingshot maneuvers, binary star systems, 3-body chaotic orbits).
2. **✨ Stellar Evolution & HR Diagram Explorer**: Interactive Hertzsprung-Russell diagram linking mass, temperature, luminosity, and fusion lifespans.
3. **🌀 Black Hole Geodesic & Event Horizon Tracer**: Tracing photon orbits and light bending around Schwarzschild and Kerr rotating black holes.

---

## 💻 2. Department of Computer Science & Information Theory (`/cs`)
*Focus: Information Theory, Machine Learning Mathematics, Quantum Computing, & Algorithm Analysis.*

### Foundational Equations & Models:
- **Information & Entropy**: Shannon Entropy ($H(X) = -\sum p(x) \log_2 p(x)$), Channel Capacity (Shannon-Hartley Theorem $C = B \log_2(1 + \text{SNR})$).
- **Machine Learning & Deep Learning**: Gradient Descent optimization ($\theta_{t+1} = \theta_t - \eta \nabla L$), Transformer self-attention ($\text{Softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$), Backpropagation matrix calculus.
- **Quantum Computing**: Qubit superposition ($|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$), Hadamard/CNOT gate matrices, Shor's and Grover's quantum algorithms.

### 🧰 Interactive Sandboxes:
1. **📡 Shannon Channel & Noise Simulator**: Demonstrates data compression and error correction over noisy communication channels.
2. **🧠 Neural Network Backpropagation Visualizer**: Interactive forward/backward pass matrix multiplication showing weights updating in real-time.
3. **⚛️ Quantum Circuit Composer**: Drag-and-drop quantum gate composer showing Bloch sphere state rotations.

---

## 🧠 3. Department of Neuroscience & Cognitive Science (`/neuroscience`)
*Focus: Biophysical Neural Networks, Synaptic Plasticity, & Psychophysics.*

### Foundational Equations & Models:
- **Neural Spiking & Circuits**: Leaky Integrate-and-Fire (LIF) models, FitzHugh-Nagumo oscillator.
- **Synaptic Learning**: Spike-Timing-Dependent Plasticity (STDP $\Delta w = f(\Delta t)$), Hebbian learning rule ($\Delta w_{ij} = \eta a_i a_j$).
- **Cognitive Psychophysics**: Weber-Fechner Law ($S = k \ln I$), Signal Detection Theory ($d'$ sensitivity index).

### 🧰 Interactive Sandboxes:
1. **⚡ Synaptic Plasticity & STDP Visualizer**: Interactive pre/post-synaptic spike timing tuner showing Long-Term Potentiation (LTP) and Depression (LTD).
2. **🧠 EEG & Neural Oscillation Frequency Explorer**: Fourier transform (FFT) decomposition of alpha, beta, theta, and gamma brainwaves.

---

## 📈 4. Department of Quantitative Economics & Econophysics (`/econophysics`)
*Focus: Mathematical Finance, Game Theory, & Complex Market Dynamics.*

### Foundational Equations & Models:
- **Options & Derivatives**: Black-Scholes partial differential equation:
  $$\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS \frac{\partial V}{\partial S} - rV = 0$$
- **Strategic Interactions**: Game Theory payoff matrices, Nash Equilibrium, Evolutionary Stable Strategies (Hawk-Dove game).
- **Statistical Econophysics**: Wealth distribution modeling using Boltzmann-Gibbs statistical mechanics and kinetic exchange models.

### 🧰 Interactive Sandboxes:
1. **📊 Black-Scholes Options & Greeks Tuner**: Real-time slider for volatility ($\sigma$), strike price, time to expiration ($t$), showing Delta, Gamma, Theta, and Vega curves.
2. **♟️ Interactive Nash Equilibrium Matrix**: 2x2 and NxN strategic payoff matrix solver with mixed strategy probability curves.

---

## ⚙️ 5. Department of Engineering & Control Theory (`/engineering`)
*Focus: Mechanics of Materials, Aerodynamics, & Dynamical Control Systems.*

### Foundational Equations & Models:
- **Control Theory**: PID Controllers ($u(t) = K_p e(t) + K_i \int e(t)dt + K_d \frac{de}{dt}$), Laplace transfer functions ($H(s)$), Bode/Nyquist stability plots.
- **Aerodynamics & Fluid Dynamics**: Bernoulli's principle, Airfoil lift & drag coefficients ($C_L, C_D$), Compressible wind tunnel shockwaves.
- **Materials Science**: Stress-strain tensor ($\sigma_{ij} = C_{ijkl} \epsilon_{kl}$), Young's Modulus ($E$), Mohr's Circle.

### 🧰 Interactive Sandboxes:
1. **🎛️ Interactive PID Controller Tuner**: Adjust proportional, integral, and derivative gains in real-time to stabilize an inverted pendulum or quadcopter position.
2. **✈️ Virtual Wind Tunnel & Airfoil Explorer**: Interactive angle-of-attack tuner displaying laminar flow lines, turbulence, and stall points.

---

## 🗺️ Long-Term Academy Expansion Blueprint

```
                                [ 🌐 PROJECT TERRA ]
                            Universal Gateway of Science
                                         │
 ┌──────────────┬──────────────┬─────────┼─────────┬──────────────┬──────────────┐
 ▼              ▼              ▼         ▼         ▼              ▼              ▼
[ ⚛️ Physics ] [ 🧪 Chem ] [ 🧬 Bio ] [ 🌍 Earth ] [ 🌌 Astro ] [ 💻 CS ] [ ⚙️ Eng / Econ ]
```

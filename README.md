<div align="center">

# ◈ AUREX

### SPATIAL INTELLIGENCE PLATFORM

<p>
  <strong>Perceive.</strong> &nbsp; 
  <strong>Understand.</strong> &nbsp; 
  <strong>Interact.</strong>
</p>

<p>
  A real-time spatial intelligence system designed to perceive environments,
  track people, interpret spatial context, and present unified intelligence
  through a premium interactive command center.
</p>

<br>

<img src="https://img.shields.io/badge/AUREX-Spatial%20Intelligence-0f172a?style=for-the-badge&logo=target&logoColor=67e8f9" alt="AUREX">
<img src="https://img.shields.io/badge/Python-3.x-0f172a?style=for-the-badge&logo=python&logoColor=67e8f9" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-Backend-0f172a?style=for-the-badge&logo=fastapi&logoColor=67e8f9" alt="FastAPI">
<img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-0f172a?style=for-the-badge&logo=opencv&logoColor=67e8f9" alt="OpenCV">

<br><br>

**REAL-TIME PERCEPTION · SPATIAL CONTEXT · INTELLIGENCE · INTERACTION**

</div>

---

## ◇ SYSTEM OVERVIEW

**AUREX** is a modular spatial intelligence platform built to transform raw environmental signals into a unified understanding of the surrounding world.

The system combines computer vision, human detection, person tracking, runtime intelligence, contextual state, security-oriented modules, and an interactive frontend into a single architecture.

Instead of presenting isolated computer-vision outputs, AUREX is designed around a **Unified World Model** — allowing different intelligence modules to contribute to one coherent representation of the environment.

```text
                    ┌─────────────────────────┐
                    │        AUREX UI         │
                    │   SPATIAL COMMAND CORE  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       API / RUNTIME      │
                    │   FastAPI Intelligence   │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │  VISION   │      │INTELLIGENCE│      │ SECURITY  │
        │   CORE    │      │    CORE    │      │   CORE    │
        └─────┬─────┘      └─────┬─────┘      └───────────┘
              │                  │
              ▼                  ▼
        ┌───────────┐      ┌──────────────┐
        │ CAMERA    │      │ WORLD MODEL  │
        │ DETECTION │      │   CONTEXT    │
        └───────────┘      └──────────────┘
```

---

## ✦ CORE CAPABILITIES

<table>
<tr>
<td width="50%">

### ◉ Spatial Perception

Real-time environmental perception powered by the AUREX vision pipeline.

- Live camera input
- Human detection
- Person tracking
- Spatial measurements
- Perception state
- Live FPS monitoring

</td>
<td width="50%">

### ◈ Unified Intelligence

Multiple intelligence signals are combined into a unified environmental state.

- People awareness
- Object awareness
- Context interpretation
- Situation state
- Priority state
- Environmental understanding

</td>
</tr>

<tr>
<td width="50%">

### ✦ AirCanvas

A spatial interaction layer designed for natural interaction with digital information through gesture-aware interfaces.

</td>
<td width="50%">

### ◎ EyeLock

Security-oriented identity and liveness intelligence designed as a modular component of the AUREX architecture.

</td>
</tr>

<tr>
<td width="50%">

### ⌁ FallGuard

Posture and movement monitoring designed for future physical-state and safety intelligence.

</td>
<td width="50%">

### ! Hazard Intelligence

A predictive analysis layer for identifying environmental risk signals and developing situations.

</td>
</tr>
</table>

---

# ◇ COMMAND CENTER

The AUREX frontend acts as a centralized **Spatial Command Center** rather than a conventional dashboard.

The interface is designed around the idea that important intelligence should remain immediately accessible.

### Primary modules

```text
01  COMMAND
02  EYELOCK
03  AIRCANVAS
04  FALLGUARD
05  HAZARDS
06  SPATIAL
07  VOICE
08  CONTEXT
09  SECURITY
10  SYSTEM CORE
```

Each module provides a dedicated interaction surface while remaining connected to the broader AUREX intelligence architecture.

---

# ◉ LIVE SPATIAL ENVIRONMENT

The command center provides a unified view of the active environment.

```text
┌──────────────────────────────────────────────┐
│ LIVE SPATIAL ENVIRONMENT                     │
├──────────────────────────────────────────────┤
│ MODE       PERCEPTION                        │
│ FEED       LIVE / STANDBY                    │
│                                              │
│ HUMAN      TRACKING ACTIVE                   │
│ OBJECT     ANALYSIS ACTIVE                   │
│ CONTEXT    ENVIRONMENT STABLE               │
│                                              │
│ AXIS X     +024.8                            │
│ AXIS Y     +018.2                            │
│ DEPTH      03.42 M                           │
│ SPACE      STABLE                            │
└──────────────────────────────────────────────┘
```

The interface is intentionally designed to feel closer to a **mission-control system** than a conventional administrative dashboard.

---

# ◈ INTELLIGENCE ARCHITECTURE

AUREX follows a modular architecture so individual intelligence systems can evolve independently without requiring the entire platform to be rebuilt.

```text
AUREX
│
├── api/
│   └── server.py
│
├── core/
│   ├── events/
│   ├── engine/
│   ├── spatial/
│   ├── intelligence/
│   ├── security/
│   ├── intent/
│   ├── emergency/
│   ├── actions/
│   └── runtime/
│
├── vision/
│   ├── camera/
│   ├── human_detector/
│   ├── person_tracker/
│   └── pose_estimator/
│
├── gesture/
│
├── identity/
│
├── voice/
│
├── frontend/
│   ├── index.html
│   ├── styles/
│   ├── scripts/
│   ├── camera/
│   └── assets/
│
└── tests/
    ├── phase3/
    └── ...
```

---

# ⚡ VISION PIPELINE

The live perception pipeline follows a simple but extensible flow:

```text
                 CAMERA
                    │
                    ▼
             FRAME CAPTURE
                    │
                    ▼
          HUMAN DETECTION
                    │
                    ▼
           PERSON TRACKING
                    │
                    ▼
        SPATIAL INTERPRETATION
                    │
                    ▼
         UNIFIED WORLD STATE
                    │
                    ▼
             COMMAND CENTER
```

This separation allows perception, intelligence, and presentation to remain independent layers.

---

# ◎ REAL-TIME CAMERA CONTROL

AUREX includes frontend camera control so the camera does not need to remain active simply because the application is running.

```text
CAMERA OFF
     │
     │ user action
     ▼
CAMERA ON
     │
     ▼
LIVE PERCEPTION
     │
     │ user action
     ▼
CAMERA OFF
     │
     ▼
CAMERA RELEASED
```

The camera controller communicates with the FastAPI backend through dedicated endpoints.

---

# ◈ API

## Health

```http
GET /api/health
```

Returns the current service health and version.

---

## Runtime Status

```http
GET /api/status
```

Returns runtime information including:

- Online state
- Camera state
- People count
- FPS
- Uptime
- Last update

---

## Camera Status

```http
GET /api/camera/status
```

Returns the current camera and perception state.

---

## Camera Stream

```http
GET /api/camera/stream
```

Provides the live MJPEG perception stream.

---

# ✦ TECHNOLOGY STACK

| Layer                | Technology                                 |
| -------------------- | ------------------------------------------ |
| Core Language        | Python                                     |
| Backend              | FastAPI                                    |
| ASGI Server          | Uvicorn                                    |
| Computer Vision      | OpenCV                                     |
| Numerical Processing | NumPy                                      |
| Frontend             | HTML / CSS / JavaScript                    |
| API Communication    | REST                                       |
| Live Video           | MJPEG Streaming                            |
| Architecture         | Modular Intelligence Pipeline              |
| Testing              | Python / unittest / custom integrity tests |

---

# ◇ DESIGN SYSTEM

AUREX uses a futuristic command-center visual language rather than a conventional web-app layout.

### Visual principles

```text
DARK SPACE
     ↓
GLASS SURFACES
     ↓
SOFT LIGHT
     ↓
DEPTH
     ↓
MOTION
     ↓
SPATIAL INFORMATION
```

The interface emphasizes:

- Deep-space backgrounds
- Glassmorphism surfaces
- Precision typography
- Cyan / ice-blue illumination
- Subtle gradients
- Spatial depth
- Animated interface elements
- Interactive command modules
- Responsive layouts
- Minimal visual noise

The goal is **technology-forward without sacrificing readability**.

---

# ✧ INTERACTION MODEL

AUREX is designed around direct interaction.

```text
             COMMAND CENTER
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    PERCEIVE     ANALYZE      ACT
       │            │            │
       └────────────┼────────────┘
                    ▼
              WORLD STATE
```

Users can move between intelligence domains without leaving the primary command environment.

---

# 🛡 SECURITY & CONTROL

Security-related components are architected as independent intelligence modules.

Current architecture includes dedicated areas for:

- Identity intelligence
- Liveness intelligence
- Trust state
- Security state
- Emergency controls
- Runtime monitoring

The modular structure allows additional verification and security mechanisms to be integrated independently.

---

# 🧠 UNIFIED WORLD MODEL

The central concept behind AUREX is the **Unified World Model**.

Instead of treating each perception result independently, the system can represent environmental information through a common state:

```text
PEOPLE
   +
OBJECTS
   +
RELATIONSHIPS
   +
ACTIVITY
   +
CONTEXT
   +
SECURITY
   +
HAZARDS
   +
INTENT
   │
   ▼
UNIFIED WORLD STATE
```

This provides the foundation for future reasoning, prediction, automation, and interaction capabilities.

---

# 🚀 FUTURE EXTENSIONS

AUREX is intentionally designed for expansion.

Potential next-generation capabilities include:

- Advanced 3D spatial mapping
- Depth-camera integration
- Multi-person pose intelligence
- Gesture-controlled interfaces
- Voice command execution
- Scene understanding
- Object relationship graphs
- Predictive activity analysis
- Advanced identity verification
- Environmental anomaly detection
- Spatial memory
- Multimodal reasoning
- Edge AI inference
- Hardware sensor integration
- Autonomous action orchestration

---

# 🧪 TESTING

AUREX includes dedicated integrity and runtime tests covering core system behavior.

Example:

```bash
py tests/phase3/test_system_integrity.py
```

The testing architecture validates important system components including:

- Module imports
- Runtime lifecycle
- Runtime cycles
- Core integrations
- System integrity

---

# ⚙️ LOCAL SETUP

## 1. Clone

```bash
git clone https://github.com/Ammarakram-dev/AUREX-Spatial-Intelligence.git
```

```bash
cd AUREX-Spatial-Intelligence
```

## 2. Install dependencies

```bash
py -m pip install -r requirements.txt
```

## 3. Start AUREX

```bash
py -m uvicorn api.server:app --host 127.0.0.1 --port 8000
```

## 4. Open the command center

```text
http://127.0.0.1:8000
```

---

# ◉ SYSTEM FLOW

```text
                 ┌───────────────────┐
                 │     ENVIRONMENT   │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │      CAMERA       │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │  COMPUTER VISION  │
                 └─────────┬─────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │   SPATIAL INTELLIGENCE   │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │    UNIFIED WORLD MODEL   │
              └────────────┬─────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        SECURITY       CONTEXT        HAZARDS
             │             │             │
             └─────────────┼─────────────┘
                           ▼
              ┌──────────────────────────┐
              │     COMMAND CENTER       │
              └──────────────────────────┘
```

---

# ✦ PROJECT STATUS

```text
╔══════════════════════════════════════════════╗
║              AUREX SYSTEM STATUS             ║
╠══════════════════════════════════════════════╣
║                                              ║
║  CORE ARCHITECTURE        ██████████  READY  ║
║  VISION PIPELINE          ██████████  READY  ║
║  PERSON TRACKING          ██████████  READY  ║
║  RUNTIME SYSTEM           ██████████  READY  ║
║  INTELLIGENCE CORE        ██████████  READY  ║
║  FASTAPI BACKEND          ██████████  READY  ║
║  COMMAND CENTER           ██████████  READY  ║
║  CAMERA CONTROL           ██████████  READY  ║
║  SYSTEM INTEGRITY         ██████████  READY  ║
║                                              ║
║              ◉ ALL SYSTEMS NOMINAL           ║
╚══════════════════════════════════════════════╝
```

---

# ◇ PROJECT PHILOSOPHY

AUREX is built around a simple idea:

> **A computer should not only process information. It should understand the environment in which that information exists.**

The project therefore treats perception, context, intelligence, security, and interaction as parts of one connected system.

---

# 👤 AUTHOR

<div align="center">

### Ammar Akram

**AI & Machine Learning · Software Engineering · Python · Data Science · AI Automation**

Building intelligent software systems and real-world technology products.

<br>

[![GitHub](https://img.shields.io/badge/GitHub-Ammarakram--dev-0f172a?style=for-the-badge&logo=github)](https://github.com/Ammarakram-dev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ammar%20Akram-0f172a?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/ammar-akram-2a30a7331)
[![Portfolio](https://img.shields.io/badge/Portfolio-Ammar%20Akram-0f172a?style=for-the-badge&logo=googlechrome)](https://ammarakram-dev.github.io/portfolio/)

</div>

---

<div align="center">

### ◈ AUREX

**SPATIAL INTELLIGENCE · PERCEPTION · CONTEXT · ACTION**

<br>

`Built to perceive the world differently.`

</div>

"use strict";

/* =========================================================
   AUREX SPATIAL INTELLIGENCE
   FRONTEND APPLICATION CORE
   ========================================================= */

const AUREX = {
  version: "1.0.0",

  apiBase: "/api",

  state: {
    bootComplete: false,

    activeModule: "overview",

    overlayOpen: false,

    notificationsOpen: false,

    cameraActive: false,

    systemOnline: true,

    emergencyMode: false,

    eyeLockState: "VERIFIED",

    airCanvasState: "READY",

    currentSituation: "Environment Stable",

    contextConfidence: 94,

    peopleCount: 1,

    objectCount: 4,

    fps: 60,

    apiConnected: false,

    cameraStream: null,

    clock: null,
  },

  elements: {},

  timers: {},

  modules: {},

  /* =====================================================
       INITIALIZATION
       ===================================================== */

  init() {
    this.cacheElements();

    this.initializeModules();

    this.bindEvents();

    this.startClock();

    this.startTelemetry();

    this.startBootSequence();

    this.initializeSpatialInteraction();

    this.updateDashboard();
  },

  /* =====================================================
       ELEMENT CACHE
       ===================================================== */

  cacheElements() {
    this.elements = {
      app: document.querySelector(".aurex-app"),

      bootScreen: document.querySelector(".boot-screen"),

      bootProgress: document.querySelector(".boot-progress-bar"),

      bootStatus: document.querySelector(".boot-status"),

      railItems: document.querySelectorAll(".rail-item"),

      moduleOverlay: document.querySelector(".module-overlay"),

      moduleWindow: document.querySelector(".module-window"),

      moduleTitle: document.querySelector(".module-header-title"),

      moduleSubtitle: document.querySelector(".module-header-subtitle"),

      moduleBody: document.querySelector(".module-body"),

      moduleClose: document.querySelector(".module-close"),

      notificationPanel: document.querySelector(".notification-panel"),

      notificationButton: document.querySelector(
        ".topbar-actions .icon-button",
      ),

      clock: document.querySelector("[data-system-time]"),

      spatialStage: document.querySelector(".spatial-stage"),

      coreObject: document.querySelector(".aurex-core-object"),

      situationMain: document.querySelector("#situation-main"),

      situationSub: document.querySelector("#situation-sub"),

      contextPeople: document.querySelector("#context-people"),

      stageMetrics: document.querySelectorAll(".stage-metric .metric-value"),

      intelligenceCards: document.querySelectorAll(".intelligence-card"),

      openModuleButtons: document.querySelectorAll("[data-open-module]"),

      quickActions: document.querySelectorAll(".quick-action"),
    };
  },

  /* =====================================================
       MODULE DEFINITIONS
       ===================================================== */

  initializeModules() {
    this.modules = {
      overview: {
        title: "Spatial Command Center",

        subtitle: "Unified perception, intelligence and action",
      },

      eyelock: {
        title: "EyeLock",

        subtitle: "Adaptive visual security and liveness",
      },

      aircanvas: {
        title: "AirCanvas",

        subtitle: "Mid-air spatial interaction",
      },

      fallguard: {
        title: "FallGuard",

        subtitle: "Human posture and fall monitoring",
      },

      hazards: {
        title: "Predictive Hazard Engine",

        subtitle: "Environmental risk and anomaly analysis",
      },

      spatial: {
        title: "Spatial Intelligence",

        subtitle: "People, objects, movement and relationships",
      },

      voice: {
        title: "Voice Intelligence",

        subtitle: "Local speech recognition and intent",
      },

      context: {
        title: "Personal Context Engine",

        subtitle: "Situation, environment and task awareness",
      },

      security: {
        title: "Security Intelligence",

        subtitle: "Multi-signal security orchestration",
      },

      system: {
        title: "AUREX System Core",

        subtitle: "Runtime, modules and system health",
      },
    };
  },

  /* =====================================================
       EVENT BINDING
       ===================================================== */

  bindEvents() {
    /* Command rail */

    this.elements.railItems.forEach((item) => {
      item.addEventListener("click", () => {
        const module = item.dataset.module;

        if (module) {
          this.openModule(module);
        }
      });
    });

    /* Cards */

    this.elements.intelligenceCards.forEach((card) => {
      card.addEventListener("click", () => {
        const module = card.dataset.openModule;

        if (module) {
          this.openModule(module);
        }
      });
    });

    /* Open module buttons */

    this.elements.openModuleButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const module = button.dataset.openModule;

        if (module) {
          this.openModule(module);
        }
      });
    });

    /* Quick actions */

    this.elements.quickActions.forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.action;

        this.executeQuickAction(action);
      });
    });

    /* Close module */

    if (this.elements.moduleClose) {
      this.elements.moduleClose.addEventListener("click", () =>
        this.closeModule(),
      );
    }

    /* Overlay click */

    if (this.elements.moduleOverlay) {
      this.elements.moduleOverlay.addEventListener("click", (event) => {
        if (event.target === this.elements.moduleOverlay) {
          this.closeModule();
        }
      });
    }

    /* Notification button */

    if (this.elements.notificationButton) {
      this.elements.notificationButton.addEventListener("click", () =>
        this.toggleNotifications(),
      );
    }

    /* Keyboard */

    document.addEventListener("keydown", (event) => {
      if (
        event.target.tagName === "INPUT" ||
        event.target.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (event.key === "Escape") {
        this.closeModule();

        this.closeNotifications();

        return;
      }

      const shortcuts = {
        1: "overview",
        2: "eyelock",
        3: "aircanvas",
        4: "fallguard",
        5: "hazards",
        6: "spatial",
        7: "voice",
        8: "context",
        9: "security",
        0: "system",
      };

      const module = shortcuts[event.key];

      if (module) {
        this.openModule(module);
      }
    });

    /* Resize */

    window.addEventListener("resize", () => this.handleResize(), {
      passive: true,
    });

    /* Visibility */

    document.addEventListener("visibilitychange", () =>
      this.handleVisibility(),
    );
  },

  /* =====================================================
       BOOT SEQUENCE
       ===================================================== */

  startBootSequence() {
    const steps = [
      {
        progress: 12,
        text: "INITIALIZING SPATIAL CORE",
      },

      {
        progress: 27,
        text: "LOADING PERCEPTION ENGINE",
      },

      {
        progress: 43,
        text: "CALIBRATING WORLD MODEL",
      },

      {
        progress: 58,
        text: "CONNECTING INTELLIGENCE LAYERS",
      },

      {
        progress: 73,
        text: "VERIFYING SECURITY SYSTEMS",
      },

      {
        progress: 87,
        text: "SYNCHRONIZING COMMAND CENTER",
      },

      {
        progress: 100,
        text: "AUREX SYSTEM ONLINE",
      },
    ];

    let index = 0;

    const executeStep = () => {
      if (index >= steps.length) {
        setTimeout(() => this.finishBoot(), 450);

        return;
      }

      const step = steps[index];

      if (this.elements.bootProgress) {
        this.elements.bootProgress.style.width = `${step.progress}%`;
      }

      if (this.elements.bootStatus) {
        this.elements.bootStatus.textContent = step.text;
      }

      index += 1;

      setTimeout(executeStep, index === steps.length ? 420 : 230);
    };

    executeStep();
  },

  finishBoot() {
    this.state.bootComplete = true;

    if (this.elements.app) {
      this.elements.app.classList.add("is-ready");

      this.elements.app.classList.add("active");
    }

    if (this.elements.bootScreen) {
      this.elements.bootScreen.classList.add("hidden");
    }

    this.animateDashboard();

    setTimeout(() => {
      this.notify(
        "AUREX ONLINE",
        "Spatial intelligence command center initialized.",
        "success",
      );
    }, 550);
  },

  animateDashboard() {
    const targets = [
      this.elements.spatialStage,

      ...this.elements.intelligenceCards,
    ];

    targets.forEach((element, index) => {
      if (!element) {
        return;
      }

      element.style.opacity = "0";

      element.style.transform = "translateY(12px) scale(.99)";

      setTimeout(
        () => {
          element.style.transition =
            "opacity 420ms cubic-bezier(.22,1,.36,1), transform 420ms cubic-bezier(.22,1,.36,1)";

          element.style.opacity = "1";

          element.style.transform = "translateY(0) scale(1)";
        },
        80 + index * 50,
      );
    });
  },

  /* =====================================================
       CLOCK
       ===================================================== */

  startClock() {
    const update = () => {
      const now = new Date();

      this.state.clock = now;

      if (this.elements.clock) {
        this.elements.clock.textContent = now.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        });
      }
    };

    update();

    this.timers.clock = setInterval(update, 1000);
  },

  /* =====================================================
       MODULE OPEN
       ===================================================== */

  openModule(moduleName) {
    const module = this.modules[moduleName];

    if (!module) {
      return;
    }

    this.state.activeModule = moduleName;

    this.state.overlayOpen = true;

    this.updateRail(moduleName);

    if (this.elements.moduleTitle) {
      this.elements.moduleTitle.textContent = module.title;
    }

    if (this.elements.moduleSubtitle) {
      this.elements.moduleSubtitle.textContent = module.subtitle;
    }

    if (this.elements.moduleBody) {
      this.elements.moduleBody.innerHTML = this.renderModule(moduleName);
    }

    if (this.elements.moduleOverlay) {
      this.elements.moduleOverlay.classList.add("open");

      this.elements.moduleOverlay.classList.add("active");
    }

    this.afterModuleRender(moduleName);
  },

  /* =====================================================
       MODULE CLOSE
       ===================================================== */

  closeModule() {
    this.state.overlayOpen = false;

    if (this.elements.moduleOverlay) {
      this.elements.moduleOverlay.classList.remove("open");

      this.elements.moduleOverlay.classList.remove("active");
    }
  },

  /* =====================================================
       RAIL STATE
       ===================================================== */

  updateRail(activeModule) {
    this.elements.railItems.forEach((item) => {
      item.classList.toggle("active", item.dataset.module === activeModule);
    });
  },

  /* =====================================================
       MODULE RENDERING
       ===================================================== */

  renderModule(moduleName) {
    switch (moduleName) {
      case "overview":
        return this.renderOverview();

      case "eyelock":
        return this.renderEyeLock();

      case "aircanvas":
        return this.renderAirCanvas();

      case "fallguard":
        return this.renderFallGuard();

      case "hazards":
        return this.renderHazards();

      case "spatial":
        return this.renderSpatial();

      case "voice":
        return this.renderVoice();

      case "context":
        return this.renderContext();

      case "security":
        return this.renderSecurity();

      case "system":
        return this.renderSystem();

      default:
        return this.renderOverview();
    }
  },

  /* =====================================================
       OVERVIEW
       ===================================================== */

  renderOverview() {
    return `

            <div class="module-content">

                <div class="data-stream">

                    <div class="active">
                        AUREX / SPATIAL COMMAND CENTER
                    </div>

                    <div>
                        Unified perception and intelligence
                        runtime active.
                    </div>

                </div>


                <div
                    class="lower-grid"
                    style="margin-top:20px"
                >

                    <section class="intelligence-panel">

                        <div class="panel-heading">

                            <div>

                                <div class="panel-title">
                                    Spatial State
                                </div>

                                <div class="panel-label">
                                    LIVE WORLD MODEL
                                </div>

                            </div>

                        </div>


                        <div class="signal-list">

                            ${this.signalRow(
                              "People detected",
                              this.state.peopleCount,
                            )}

                            ${this.signalRow(
                              "Objects tracked",
                              this.state.objectCount,
                            )}

                            ${this.signalRow(
                              "Context confidence",
                              `${this.state.contextConfidence}%`,
                            )}

                            ${this.signalRow(
                              "Security",
                              this.state.eyeLockState,
                            )}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-heading">

                            <div class="panel-title">
                                Runtime
                            </div>

                            <div class="panel-label">
                                ONLINE
                            </div>

                        </div>


                        <div class="health-list">

                            ${this.healthRow("Perception", "96%")}

                            ${this.healthRow("Intelligence", "94%")}

                            ${this.healthRow("Security", "99%")}

                            ${this.healthRow("Runtime", "98%")}

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       EYELOCK
       ===================================================== */

  renderEyeLock() {
    return `

            <div class="module-content">

                <div class="camera-surface">

                    <video
                        id="aurex-camera"
                        autoplay
                        muted
                        playsinline
                    ></video>

                    <div class="camera-overlay"></div>

                    <div class="camera-scan"></div>

                </div>


                <div
                    class="lower-grid"
                    style="margin-top:14px"
                >

                    <section class="intelligence-panel">

                        <div class="panel-heading">

                            <div>

                                <div class="panel-title">
                                    EyeLock State
                                </div>

                                <div class="panel-label">
                                    MULTI-SIGNAL SECURITY
                                </div>

                            </div>

                        </div>


                        <div class="situation-display">

                            <div class="situation-orb"></div>

                            <div>

                                <div
                                    class="situation-main"
                                    id="eyelock-module-state"
                                >
                                    ${this.state.eyeLockState}
                                </div>

                                <div class="situation-sub">
                                    Identity and liveness
                                    monitoring
                                </div>

                            </div>

                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Identity", "MONITORING")}

                            ${this.signalRow("Liveness", "ACTIVE")}

                            ${this.signalRow("Blink signal", "READY")}

                            ${this.signalRow("Head movement", "TRACKING")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Controls
                        </div>


                        <div
                            style="
                                display:flex;
                                flex-wrap:wrap;
                                gap:8px;
                                margin-top:20px;
                            "
                        >

                            <button
                                class="panel-link"
                                data-module-action="camera"
                                type="button"
                            >
                                START CAMERA
                            </button>

                            <button
                                class="panel-link"
                                data-module-action="simulate-lock"
                                type="button"
                            >
                                VALIDATE SIGNAL
                            </button>

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       AIRCANVAS
       ===================================================== */

  renderAirCanvas() {
    return `

            <div class="module-content">

                <div class="aircanvas-stage">

                    <div class="depth-grid"></div>

                    <div class="aircanvas-object"></div>

                    <div class="aircanvas-hint">
                        HAND TRACKING READY ·
                        SPATIAL INTERACTION SURFACE INITIALIZED
                    </div>

                </div>


                <div
                    class="lower-grid"
                    style="margin-top:14px"
                >

                    <section class="intelligence-panel">

                        <div class="panel-heading">

                            <div class="panel-title">
                                Gesture Engine
                            </div>

                            <div class="panel-label">
                                READY
                            </div>

                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Hand detection", "READY")}

                            ${this.signalRow("Gesture tracking", "READY")}

                            ${this.signalRow("Spatial cursor", "ACTIVE")}

                            ${this.signalRow("3D manipulation", "READY")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Available Gestures
                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Open palm", "SELECT")}

                            ${this.signalRow("Pinch", "GRAB")}

                            ${this.signalRow("Swipe", "MOVE")}

                            ${this.signalRow("Two-hand scale", "RESIZE")}

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       FALLGUARD
       ===================================================== */

  renderFallGuard() {
    return `

            <div class="module-content">

                <div class="camera-surface">

                    <video
                        id="fallguard-camera"
                        autoplay
                        muted
                        playsinline
                    ></video>

                    <div class="camera-overlay"></div>

                    <div class="camera-scan"></div>

                </div>


                <div
                    class="lower-grid"
                    style="margin-top:14px"
                >

                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Posture Intelligence
                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Human detection", "ACTIVE")}

                            ${this.signalRow("Pose estimation", "ACTIVE")}

                            ${this.signalRow("Movement analysis", "ACTIVE")}

                            ${this.signalRow("Fall assessment", "MONITORING")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Safety State
                        </div>


                        <div class="situation-display">

                            <div class="situation-orb"></div>

                            <div>

                                <div class="situation-main">
                                    NORMAL
                                </div>

                                <div class="situation-sub">
                                    No current fall event
                                    detected
                                </div>

                            </div>

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       HAZARDS
       ===================================================== */

  renderHazards() {
    return `

            <div class="module-content">

                <div class="lower-grid">

                    <section class="intelligence-panel">

                        <div class="panel-heading">

                            <div class="panel-title">
                                Predictive Hazard Engine
                            </div>

                            <div class="panel-label">
                                CONTINUOUS ANALYSIS
                            </div>

                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Environmental state", "STABLE")}

                            ${this.signalRow("Movement anomaly", "NONE")}

                            ${this.signalRow("Spatial conflict", "NONE")}

                            ${this.signalRow("Risk trajectory", "LOW")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Current Risk
                        </div>


                        <div class="situation-display">

                            <div class="situation-orb"></div>

                            <div>

                                <div class="situation-main">
                                    LOW
                                </div>

                                <div class="situation-sub">
                                    No immediate hazard
                                    escalation
                                </div>

                            </div>

                        </div>

                    </section>

                </div>


                <section
                    class="intelligence-panel"
                    style="margin-top:14px"
                >

                    <div class="panel-title">
                        Hazard Pipeline
                    </div>


                    <div class="health-list">

                        ${this.healthRow("Perception", "97%")}

                        ${this.healthRow("Temporal memory", "93%")}

                        ${this.healthRow("Prediction", "91%")}

                        ${this.healthRow("Emergency layer", "99%")}

                    </div>

                </section>

            </div>

        `;
  },

  /* =====================================================
       SPATIAL
       ===================================================== */

  renderSpatial() {
    return `

            <div class="module-content">

                <div
                    class="spatial-stage module-spatial-stage"
                    style="min-height:500px"
                >

                    <div class="depth-grid"></div>

                    <div class="scan-plane"></div>

                    <div class="horizon"></div>


                    <div
                        class="aurex-core-object module-core"
                    >

                        <div class="orbit-ring"></div>
                        <div class="orbit-ring"></div>
                        <div class="orbit-ring"></div>

                        <div class="core-cube">

                            <div class="cube-face cube-front"></div>
                            <div class="cube-face cube-back"></div>
                            <div class="cube-face cube-right"></div>
                            <div class="cube-face cube-left"></div>
                            <div class="cube-face cube-top"></div>
                            <div class="cube-face cube-bottom"></div>

                        </div>

                        <div class="core-energy"></div>

                    </div>


                    <div class="spatial-node node-human">

                        <div class="node-header">

                            <span class="node-dot"></span>

                            <span class="node-title">
                                HUMAN
                            </span>

                        </div>

                        <div class="node-data">
                            TRACK #01<br>
                            MOVEMENT: ACTIVE
                        </div>

                    </div>


                    <div class="spatial-node node-object">

                        <div class="node-header">

                            <span class="node-dot violet"></span>

                            <span class="node-title">
                                OBJECTS
                            </span>

                        </div>

                        <div class="node-data">
                            ${this.state.objectCount}
                            TRACKED<br>
                            RELATIONS: ACTIVE
                        </div>

                    </div>


                    <div class="spatial-node node-context">

                        <div class="node-header">

                            <span class="node-dot green"></span>

                            <span class="node-title">
                                CONTEXT
                            </span>

                        </div>

                        <div class="node-data">
                            CONFIDENCE:
                            ${this.state.contextConfidence}%
                        </div>

                    </div>

                </div>

            </div>

        `;
  },

  /* =====================================================
       VOICE
       ===================================================== */

  renderVoice() {
    return `

            <div class="module-content">

                <section class="intelligence-panel">

                    <div class="panel-heading">

                        <div>

                            <div class="panel-title">
                                Voice Intelligence
                            </div>

                            <div class="panel-label">
                                LOCAL RECOGNITION PIPELINE
                            </div>

                        </div>

                        <div class="card-state">
                            READY
                        </div>

                    </div>


                    <div class="situation-display">

                        <div class="situation-orb"></div>

                        <div>

                            <div class="situation-main">
                                LISTENING
                            </div>

                            <div class="situation-sub">
                                Local speech recognition
                                pipeline ready
                            </div>

                        </div>

                    </div>


                    <div
                        style="
                            display:flex;
                            gap:12px;
                            margin-top:22px;
                            flex-wrap:wrap;
                        "
                    >

                        <button
                            class="panel-link"
                            data-module-action="voice"
                            type="button"
                        >
                            START VOICE
                        </button>

                        <button
                            class="panel-link"
                            data-module-action="voice-command"
                            type="button"
                        >
                            COMMAND TEST
                        </button>

                    </div>

                </section>

            </div>

        `;
  },

  /* =====================================================
       CONTEXT
       ===================================================== */

  renderContext() {
    return `

            <div class="module-content">

                <div class="lower-grid">

                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Current Situation
                        </div>


                        <div class="situation-display">

                            <div class="situation-orb"></div>

                            <div>

                                <div class="situation-main">
                                    ${this.state.currentSituation}
                                </div>

                                <div class="situation-sub">
                                    Environment currently
                                    understood
                                </div>

                            </div>

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Context Confidence
                        </div>


                        <div
                            style="
                                margin-top:28px;
                                font-family:'Space Grotesk';
                                font-size:42px;
                                color:var(--cyan);
                            "
                        >
                            ${this.state.contextConfidence}%
                        </div>


                        <div
                            style="
                                margin-top:8px;
                                color:var(--text-dim);
                                font-size:9px;
                            "
                        >
                            Unified contextual confidence
                        </div>

                    </section>

                </div>


                <section
                    class="intelligence-panel"
                    style="margin-top:14px"
                >

                    <div class="panel-title">
                        Context Signals
                    </div>


                    <div class="signal-list">

                        ${this.signalRow("Environment", "STABLE")}

                        ${this.signalRow("Activity", "NORMAL")}

                        ${this.signalRow("Task state", "AVAILABLE")}

                        ${this.signalRow("Temporal state", "CURRENT")}

                    </div>

                </section>

            </div>

        `;
  },

  /* =====================================================
       SECURITY
       ===================================================== */

  renderSecurity() {
    return `

            <div class="module-content">

                <div class="lower-grid">

                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Security Intelligence
                        </div>


                        <div class="signal-list">

                            ${this.signalRow("PresenceLock", "ACTIVE")}

                            ${this.signalRow("ShadowLock", "READY")}

                            ${this.signalRow("TrustLock", "ACTIVE")}

                            ${this.signalRow("IntentLock", "READY")}

                            ${this.signalRow("GuardianLock", "STANDBY")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Security State
                        </div>


                        <div class="situation-display">

                            <div class="situation-orb"></div>

                            <div>

                                <div class="situation-main">
                                    ${this.state.eyeLockState}
                                </div>

                                <div class="situation-sub">
                                    Multi-signal security active
                                </div>

                            </div>

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       SYSTEM
       ===================================================== */

  renderSystem() {
    return `

            <div class="module-content">

                <div class="lower-grid">

                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Runtime Health
                        </div>


                        <div class="health-list">

                            ${this.healthRow("Runtime", "98%")}

                            ${this.healthRow("Perception", "96%")}

                            ${this.healthRow("Intelligence", "94%")}

                            ${this.healthRow("Security", "99%")}

                            ${this.healthRow("Action layer", "97%")}

                        </div>

                    </section>


                    <section class="intelligence-panel">

                        <div class="panel-title">
                            Runtime State
                        </div>


                        <div class="signal-list">

                            ${this.signalRow("Status", "RUNNING")}

                            ${this.signalRow("Mode", "PRODUCTION")}

                            ${this.signalRow("Version", this.version)}

                            ${this.signalRow(
                              "API",
                              this.state.apiConnected ? "CONNECTED" : "STANDBY",
                            )}

                        </div>

                    </section>

                </div>

            </div>

        `;
  },

  /* =====================================================
       HELPERS
       ===================================================== */

  signalRow(name, value) {
    return `

            <div class="signal-row">

                <span class="signal-name">
                    ${this.escapeHTML(name)}
                </span>

                <span class="signal-value">
                    ${this.escapeHTML(String(value))}
                </span>

            </div>

        `;
  },

  healthRow(name, value) {
    const numeric = parseInt(String(value).replace("%", ""), 10) || 0;

    return `

            <div class="health-row">

                <span class="health-name">
                    ${this.escapeHTML(name)}
                </span>

                <div class="health-bar">

                    <span
                        style="width:${numeric}%"
                    ></span>

                </div>

                <span class="health-value">
                    ${numeric}%
                </span>

            </div>

        `;
  },

  /* =====================================================
       MODULE ACTIONS
       ===================================================== */

  afterModuleRender(moduleName) {
    if (!this.elements.moduleBody) {
      return;
    }

    this.elements.moduleBody
      .querySelectorAll("[data-module-action]")
      .forEach((button) => {
        button.addEventListener("click", () => {
          this.executeModuleAction(button.dataset.moduleAction);
        });
      });

    if (moduleName === "spatial") {
      this.initializeModuleSpatialInteraction();
    }
  },

  executeModuleAction(action) {
    switch (action) {
      case "camera":
        this.startCamera();

        break;

      case "simulate-lock":
        this.validateSecuritySignal();

        break;

      case "voice":
        this.startVoice();

        break;

      case "voice-command":
        this.testVoiceCommand();

        break;

      default:
        this.notify("MODULE ACTION", `${action} requested.`, "info");
    }
  },

  /* =====================================================
       QUICK ACTIONS
       ===================================================== */

  executeQuickAction(action) {
    switch (action) {
      case "aircanvas":
        this.openModule("aircanvas");

        break;

      case "voice":
        this.openModule("voice");

        break;

      case "emergency":
        this.activateEmergency();

        break;

      default:
        this.notify("ACTION", `${action} requested.`, "info");
    }
  },

  /* =====================================================
       EMERGENCY
       ===================================================== */

  activateEmergency() {
    this.state.emergencyMode = true;

    this.notify(
      "EMERGENCY WORKFLOW",
      "Emergency controls opened for confirmation.",
      "warning",
    );

    this.openModule("hazards");
  },

  /* =====================================================
       EYELOCK VALIDATION
       ===================================================== */

  validateSecuritySignal() {
    const state = document.querySelector("#eyelock-module-state");

    if (!state) {
      return;
    }

    state.textContent = "VALIDATING";

    setTimeout(() => {
      state.textContent = "VERIFIED";

      this.state.eyeLockState = "VERIFIED";

      this.notify("EYELOCK", "Security validation cycle completed.", "success");
    }, 900);
  },

  /* =====================================================
       CAMERA
       ===================================================== */

  async startCamera() {
    const video =
      document.querySelector("#aurex-camera") ||
      document.querySelector("#fallguard-camera");

    if (!video) {
      this.notify("CAMERA", "No camera surface available.", "warning");

      return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.notify(
        "CAMERA",
        "Camera API is unavailable in this browser context.",
        "danger",
      );

      return;
    }

    try {
      this.stopCamera();

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: {
            ideal: 1280,
          },

          height: {
            ideal: 720,
          },

          facingMode: "user",
        },

        audio: false,
      });

      video.srcObject = stream;

      this.state.cameraStream = stream;

      await video.play();

      this.state.cameraActive = true;

      this.notify("CAMERA ACTIVE", "Live visual stream connected.", "success");
    } catch (error) {
      console.error("AUREX camera error:", error);

      this.notify(
        "CAMERA ACCESS",
        "Camera permission was not granted or the device is unavailable.",
        "danger",
      );
    }
  },

  stopCamera() {
    if (this.state.cameraStream) {
      this.state.cameraStream.getTracks().forEach((track) => track.stop());

      this.state.cameraStream = null;
    }

    document.querySelectorAll("video").forEach((video) => {
      if (video.srcObject) {
        video.srcObject.getTracks().forEach((track) => track.stop());

        video.srcObject = null;
      }
    });

    this.state.cameraActive = false;
  },

  /* =====================================================
       VOICE
       ===================================================== */

  startVoice() {
    const Recognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Recognition) {
      this.notify(
        "VOICE",
        "Browser speech recognition is unavailable. AUREX local voice pipeline remains ready.",
        "warning",
      );

      return;
    }

    const recognition = new Recognition();

    recognition.lang = "en-US";

    recognition.interimResults = true;

    recognition.continuous = false;

    recognition.onstart = () => {
      this.notify("VOICE", "Listening for a command...", "info");
    };

    recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1];

      const transcript = result[0].transcript;

      this.notify("VOICE COMMAND", transcript, "success");

      this.processVoiceIntent(transcript);
    };

    recognition.onerror = () => {
      this.notify("VOICE", "Voice recognition ended.", "warning");
    };

    try {
      recognition.start();
    } catch (error) {
      console.debug("Voice start:", error);
    }
  },

  testVoiceCommand() {
    this.notify("VOICE TEST", "Voice intent pipeline is ready.", "success");
  },

  processVoiceIntent(text) {
    const normalized = String(text).toLowerCase();

    if (normalized.includes("air canvas") || normalized.includes("aircanvas")) {
      this.openModule("aircanvas");

      return;
    }

    if (
      normalized.includes("security") ||
      normalized.includes("eye lock") ||
      normalized.includes("eyelock")
    ) {
      this.openModule("security");

      return;
    }

    if (normalized.includes("hazard") || normalized.includes("danger")) {
      this.openModule("hazards");

      return;
    }

    if (normalized.includes("camera") || normalized.includes("vision")) {
      this.openModule("eyelock");

      return;
    }

    if (normalized.includes("fall")) {
      this.openModule("fallguard");

      return;
    }

    if (normalized.includes("spatial")) {
      this.openModule("spatial");

      return;
    }

    this.notify(
      "INTENT",
      "Command received. Backend action mapping is ready for integration.",
      "info",
    );
  },

  /* =====================================================
       TELEMETRY
       ===================================================== */

  startTelemetry() {
    this.timers.telemetry = setInterval(() => {
      this.updateTelemetry();
    }, 1800);
  },

  updateTelemetry() {
    if (!this.state.bootComplete) {
      return;
    }

    /*
     * These values are frontend demonstration telemetry.
     * They are intentionally not presented as real sensor
     * measurements until the backend is connected.
     */

    if (!this.state.apiConnected) {
      this.state.peopleCount = Math.max(
        1,
        Math.min(4, this.state.peopleCount + Math.round(Math.random() * 2 - 1)),
      );

      this.state.objectCount = Math.max(
        2,
        Math.min(9, this.state.objectCount + Math.round(Math.random() * 2 - 1)),
      );

      this.state.contextConfidence = Math.max(
        88,
        Math.min(
          98,
          this.state.contextConfidence + Math.round(Math.random() * 2 - 1),
        ),
      );
    }

    this.updateDashboard();
  },

  /* =====================================================
       DASHBOARD UPDATE
       ===================================================== */

  updateDashboard() {
    const values = this.elements.stageMetrics;

    if (values && values.length >= 3) {
      if (values[0]) {
        values[0].textContent = `${this.state.peopleCount}`;
      }

      if (values[1]) {
        values[1].textContent = `${this.state.objectCount}`;
      }

      if (values[2]) {
        values[2].textContent = `${this.state.contextConfidence}%`;
      }
    }

    if (this.elements.contextPeople) {
      this.elements.contextPeople.textContent = String(
        this.state.peopleCount,
      ).padStart(2, "0");
    }

    if (this.elements.situationMain) {
      this.elements.situationMain.textContent = this.state.currentSituation;
    }

    if (this.elements.situationSub) {
      this.elements.situationSub.textContent = this.state.apiConnected
        ? "Live backend intelligence connected."
        : "AUREX is observing the environment interface in standby mode.";
    }
  },

  /* =====================================================
       3D SPATIAL INTERACTION
       ===================================================== */

  initializeSpatialInteraction() {
    const stage = this.elements.spatialStage;

    const core = this.elements.coreObject;

    if (!stage || !core) {
      return;
    }

    let targetX = 0;

    let targetY = 0;

    let currentX = 0;

    let currentY = 0;

    stage.addEventListener(
      "pointermove",
      (event) => {
        const rect = stage.getBoundingClientRect();

        const x = (event.clientX - rect.left) / rect.width;

        const y = (event.clientY - rect.top) / rect.height;

        targetX = (x - 0.5) * 18;

        targetY = (y - 0.5) * -14;
      },
      {
        passive: true,
      },
    );

    stage.addEventListener(
      "pointerleave",
      () => {
        targetX = 0;

        targetY = 0;
      },
      {
        passive: true,
      },
    );

    const animate = () => {
      currentX += (targetX - currentX) * 0.075;

      currentY += (targetY - currentY) * 0.075;

      core.style.marginLeft = `${currentX}px`;

      core.style.marginTop = `${currentY}px`;

      requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  },

  /* =====================================================
       MODULE 3D INTERACTION
       ===================================================== */

  initializeModuleSpatialInteraction() {
    const stage = document.querySelector(".module-spatial-stage");

    const core = stage?.querySelector(".module-core");

    if (!stage || !core) {
      return;
    }

    let targetX = 0;

    let targetY = 0;

    let currentX = 0;

    let currentY = 0;

    stage.addEventListener(
      "pointermove",
      (event) => {
        const rect = stage.getBoundingClientRect();

        const x = (event.clientX - rect.left) / rect.width;

        const y = (event.clientY - rect.top) / rect.height;

        targetX = (x - 0.5) * 20;

        targetY = (y - 0.5) * -16;
      },
      {
        passive: true,
      },
    );

    stage.addEventListener(
      "pointerleave",
      () => {
        targetX = 0;

        targetY = 0;
      },
      {
        passive: true,
      },
    );

    const animate = () => {
      currentX += (targetX - currentX) * 0.08;

      currentY += (targetY - currentY) * 0.08;

      core.style.marginLeft = `${currentX}px`;

      core.style.marginTop = `${currentY}px`;

      requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  },

  /* =====================================================
       NOTIFICATIONS
       ===================================================== */

  toggleNotifications() {
    if (!this.elements.notificationPanel) {
      return;
    }

    this.state.notificationsOpen = !this.state.notificationsOpen;

    this.elements.notificationPanel.style.pointerEvents = this.state
      .notificationsOpen
      ? "auto"
      : "none";

    if (!this.state.notificationsOpen) {
      return;
    }

    this.notify(
      "SYSTEM NOTIFICATIONS",
      "AUREX command center is operating normally.",
      "info",
    );
  },

  closeNotifications() {
    this.state.notificationsOpen = false;

    if (this.elements.notificationPanel) {
      this.elements.notificationPanel.style.pointerEvents = "none";
    }
  },

  notify(title, message, type = "info") {
    console.log(`[AUREX:${type.toUpperCase()}]`, title, message);

    const panel = this.elements.notificationPanel;

    if (!panel) {
      return;
    }

    const item = document.createElement("div");

    item.className = "notification-item";

    const icon = document.createElement("div");

    icon.className = "notification-icon";

    icon.textContent =
      type === "success"
        ? "✓"
        : type === "warning"
          ? "!"
          : type === "danger"
            ? "×"
            : "•";

    const content = document.createElement("div");

    const heading = document.createElement("div");

    heading.className = "notification-title";

    heading.textContent = title;

    const body = document.createElement("div");

    body.className = "notification-text";

    body.textContent = message;

    content.appendChild(heading);

    content.appendChild(body);

    item.appendChild(icon);

    item.appendChild(content);

    panel.prepend(item);

    while (panel.children.length > 5) {
      panel.removeChild(panel.lastElementChild);
    }

    setTimeout(() => {
      if (item.parentElement === panel && !this.state.notificationsOpen) {
        item.remove();
      }
    }, 7000);
  },

  /* =====================================================
       BACKEND API
       ===================================================== */

  async apiRequest(endpoint, options = {}) {
    const url = `${this.apiBase}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",

          ...(options.headers || {}),
        },

        ...options,
      });

      if (!response.ok) {
        throw new Error(`API ${response.status}`);
      }

      this.state.apiConnected = true;

      return await response.json();
    } catch (error) {
      this.state.apiConnected = false;

      console.debug("AUREX API:", error.message);

      return null;
    }
  },

  async connectBackend() {
    const result = await this.apiRequest("/health");

    if (result) {
      this.state.apiConnected = true;

      this.notify(
        "BACKEND CONNECTED",
        "AUREX production API is responding.",
        "success",
      );

      this.updateDashboard();
    }
  },

  /* =====================================================
       RESIZE
       ===================================================== */

  handleResize() {
    if (window.innerWidth < 760 && this.state.overlayOpen) {
      return;
    }
  },

  /* =====================================================
       VISIBILITY
       ===================================================== */

  handleVisibility() {
    if (document.hidden) {
      return;
    }

    this.updateDashboard();
  },

  /* =====================================================
       HTML ESCAPE
       ===================================================== */

  escapeHTML(value) {
    return String(value)
      .replaceAll("&", "&amp;")

      .replaceAll("<", "&lt;")

      .replaceAll(">", "&gt;")

      .replaceAll('"', "&quot;")

      .replaceAll("'", "&#039;");
  },

  /* =====================================================
       CLEANUP
       ===================================================== */

  destroy() {
    Object.values(this.timers).forEach((timer) => {
      clearInterval(timer);

      clearTimeout(timer);
    });

    this.stopCamera();
  },
};

/* =========================================================
   START AUREX
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  AUREX.init();

  setTimeout(() => {
    AUREX.connectBackend();
  }, 1800);
});

/* =========================================================
   GLOBAL ERROR HANDLING
   ========================================================= */

window.addEventListener("error", (event) => {
  console.error("AUREX frontend error:", event.error || event.message);
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("AUREX async error:", event.reason);
});

/* =========================================================
   PUBLIC API
   ========================================================= */

window.AUREX = AUREX;
/* ============================================================
   AUREX LIVE BACKEND INTEGRATION
   Real camera + perception + telemetry
   ============================================================ */

(() => {
  "use strict";

  const API_BASE = "/api";
  const CAMERA_STREAM = `${API_BASE}/camera/stream`;

  let livePollTimer = null;
  let cameraOnline = false;

  const liveState = {
    online: false,
    camera: false,
    people: 0,
    objects: 0,
    fps: 0,
    uptime: 0,
  };

  function escapeHTML(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function moduleIsOpen() {
    const overlay = document.querySelector(".module-overlay");

    if (!overlay) return false;

    const style = window.getComputedStyle(overlay);

    return style.display !== "none" && overlay.classList.contains("active");
  }

  function getModuleName() {
    const title =
      document.querySelector(".module-header-title")?.textContent || "";

    return title.toLowerCase();
  }

  function shouldShowCamera() {
    const name = getModuleName();

    return (
      name.includes("spatial") ||
      name.includes("fall") ||
      name.includes("overview") ||
      name.includes("aircanvas") ||
      name.includes("scene") ||
      name.includes("security") ||
      name.includes("eyelock")
    );
  }

  function createLivePanel() {
    const body = document.querySelector(".module-body");

    if (!body) return null;

    let panel = document.getElementById("aurex-live-panel");

    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "aurex-live-panel";
    panel.className = "aurex-live-panel";

    panel.innerHTML = `
            <div class="aurex-live-header">
                <div>
                    <div class="aurex-live-kicker">
                        AUREX // REAL-TIME PERCEPTION
                    </div>

                    <div class="aurex-live-title">
                        Spatial Vision
                    </div>
                </div>

                <div class="aurex-live-status" id="aurex-live-status">
                    <span class="aurex-status-dot"></span>
                    CONNECTING
                </div>
            </div>

            <div class="aurex-live-viewport">
                <img
                    id="aurex-camera-feed"
                    class="aurex-camera-feed"
                    src="${CAMERA_STREAM}"
                    alt="AUREX live spatial perception"
                />

                <div class="aurex-camera-grid"></div>

                <div class="aurex-camera-corner top-left"></div>
                <div class="aurex-camera-corner top-right"></div>
                <div class="aurex-camera-corner bottom-left"></div>
                <div class="aurex-camera-corner bottom-right"></div>

                <div class="aurex-live-label">
                    LIVE // CAMERA 01
                </div>

                <div class="aurex-live-fps" id="aurex-live-fps">
                    0 FPS
                </div>

                <div
                    class="aurex-camera-message"
                    id="aurex-camera-message"
                >
                    INITIALIZING PERCEPTION...
                </div>
            </div>

            <div class="aurex-live-metrics">

                <div class="aurex-live-metric">
                    <span class="metric-label">PEOPLE</span>
                    <strong id="aurex-people-count">0</strong>
                </div>

                <div class="aurex-live-metric">
                    <span class="metric-label">OBJECTS</span>
                    <strong id="aurex-object-count">0</strong>
                </div>

                <div class="aurex-live-metric">
                    <span class="metric-label">FPS</span>
                    <strong id="aurex-fps-value">0</strong>
                </div>

                <div class="aurex-live-metric">
                    <span class="metric-label">CAMERA</span>
                    <strong id="aurex-camera-state">OFFLINE</strong>
                </div>

            </div>

            <div class="aurex-live-footer">

                <div class="aurex-live-indicator">
                    <span class="aurex-pulse"></span>
                    PERCEPTION ENGINE
                </div>

                <div id="aurex-runtime-uptime">
                    Runtime 0s
                </div>

            </div>
        `;

    body.prepend(panel);

    installLivePanelStyles();

    const feed = document.getElementById("aurex-camera-feed");

    if (feed) {
      feed.onload = () => {
        cameraOnline = true;
        updateCameraVisualState(true);
      };

      feed.onerror = () => {
        cameraOnline = false;
        updateCameraVisualState(false);
      };
    }

    return panel;
  }

  function installLivePanelStyles() {
    if (document.getElementById("aurex-live-styles")) {
      return;
    }

    const style = document.createElement("style");
    style.id = "aurex-live-styles";

    style.textContent = `
            .aurex-live-panel {
                width: 100%;
                margin-bottom: 24px;
                border: 1px solid rgba(130, 190, 255, .18);
                border-radius: 18px;
                overflow: hidden;
                background:
                    linear-gradient(
                        135deg,
                        rgba(255,255,255,.055),
                        rgba(20,30,48,.78)
                    );
                box-shadow:
                    0 25px 80px rgba(0,0,0,.35),
                    inset 0 1px rgba(255,255,255,.08);
                animation: aurexPanelIn .35s ease both;
            }

            .aurex-live-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 20px;
                padding: 18px 20px;
                border-bottom: 1px solid rgba(255,255,255,.08);
            }

            .aurex-live-kicker {
                font-size: 9px;
                letter-spacing: .24em;
                color: rgba(150,205,255,.72);
                margin-bottom: 5px;
            }

            .aurex-live-title {
                font-size: 18px;
                font-weight: 650;
                letter-spacing: -.02em;
            }

            .aurex-live-status {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 9px;
                letter-spacing: .18em;
                color: rgba(255,255,255,.7);
                white-space: nowrap;
            }

            .aurex-status-dot {
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: #ff6b6b;
                box-shadow: 0 0 14px rgba(255,107,107,.8);
            }

            .aurex-live-status.online .aurex-status-dot {
                background: #55e6a5;
                box-shadow: 0 0 16px rgba(85,230,165,.9);
            }

            .aurex-live-viewport {
                position: relative;
                width: 100%;
                min-height: 360px;
                aspect-ratio: 16 / 9;
                overflow: hidden;
                background: #05080d;
            }

            .aurex-camera-feed {
                position: absolute;
                inset: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
                filter:
                    contrast(1.04)
                    brightness(.94)
                    saturate(.88);
            }

            .aurex-camera-grid {
                position: absolute;
                inset: 0;
                pointer-events: none;
                opacity: .16;
                background:
                    linear-gradient(
                        rgba(150,210,255,.18) 1px,
                        transparent 1px
                    ),
                    linear-gradient(
                        90deg,
                        rgba(150,210,255,.18) 1px,
                        transparent 1px
                    );
                background-size: 50px 50px;
                mix-blend-mode: screen;
            }

            .aurex-camera-corner {
                position: absolute;
                width: 32px;
                height: 32px;
                border-color: rgba(155,215,255,.9);
                border-style: solid;
                opacity: .8;
            }

            .aurex-camera-corner.top-left {
                top: 18px;
                left: 18px;
                border-width: 2px 0 0 2px;
            }

            .aurex-camera-corner.top-right {
                top: 18px;
                right: 18px;
                border-width: 2px 2px 0 0;
            }

            .aurex-camera-corner.bottom-left {
                bottom: 18px;
                left: 18px;
                border-width: 0 0 2px 2px;
            }

            .aurex-camera-corner.bottom-right {
                bottom: 18px;
                right: 18px;
                border-width: 0 2px 2px 0;
            }

            .aurex-live-label,
            .aurex-live-fps {
                position: absolute;
                top: 18px;
                padding: 7px 10px;
                border-radius: 7px;
                background: rgba(4,8,14,.68);
                border: 1px solid rgba(255,255,255,.1);
                backdrop-filter: blur(10px);
                font-size: 9px;
                letter-spacing: .14em;
                color: rgba(240,247,255,.82);
            }

            .aurex-live-label {
                left: 60px;
            }

            .aurex-live-fps {
                right: 60px;
            }

            .aurex-camera-message {
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                padding: 10px 15px;
                border-radius: 8px;
                background: rgba(3,7,13,.72);
                border: 1px solid rgba(160,210,255,.15);
                color: rgba(235,245,255,.7);
                font-size: 10px;
                letter-spacing: .16em;
                pointer-events: none;
                transition: opacity .25s ease;
            }

            .aurex-live-metrics {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                border-top: 1px solid rgba(255,255,255,.07);
            }

            .aurex-live-metric {
                padding: 16px 18px;
                border-right: 1px solid rgba(255,255,255,.07);
            }

            .aurex-live-metric:last-child {
                border-right: 0;
            }

            .aurex-live-metric .metric-label {
                display: block;
                font-size: 8px;
                letter-spacing: .16em;
                color: rgba(190,205,225,.52);
                margin-bottom: 7px;
            }

            .aurex-live-metric strong {
                font-size: 20px;
                font-weight: 600;
                color: rgba(245,249,255,.94);
            }

            .aurex-live-footer {
                display: flex;
                justify-content: space-between;
                padding: 11px 18px;
                border-top: 1px solid rgba(255,255,255,.06);
                font-size: 8px;
                letter-spacing: .12em;
                color: rgba(180,200,225,.5);
            }

            .aurex-live-indicator {
                display: flex;
                align-items: center;
                gap: 7px;
            }

            .aurex-pulse {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #55e6a5;
                box-shadow: 0 0 10px rgba(85,230,165,.8);
                animation: aurexPulse 1.5s infinite;
            }

            @keyframes aurexPulse {
                0%,100% { opacity: .45; transform: scale(.8); }
                50% { opacity: 1; transform: scale(1.15); }
            }

            @keyframes aurexPanelIn {
                from {
                    opacity: 0;
                    transform: translateY(10px) scale(.99);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            @media (max-width: 700px) {
                .aurex-live-metrics {
                    grid-template-columns: repeat(2, 1fr);
                }

                .aurex-live-metric:nth-child(2) {
                    border-right: 0;
                }

                .aurex-live-viewport {
                    min-height: 230px;
                }

                .aurex-live-header {
                    align-items: flex-start;
                }
            }
        `;

    document.head.appendChild(style);
  }

  function updateCameraVisualState(active) {
    const status = document.getElementById("aurex-live-status");
    const state = document.getElementById("aurex-camera-state");
    const message = document.getElementById("aurex-camera-message");

    if (status) {
      status.classList.toggle("online", active);
      status.innerHTML = `
                <span class="aurex-status-dot"></span>
                ${active ? "LIVE" : "CONNECTING"}
            `;
    }

    if (state) {
      state.textContent = active ? "LIVE" : "OFFLINE";
    }

    if (message) {
      message.style.opacity = active ? "0" : "1";
    }
  }

  async function fetchRuntimeStatus() {
    try {
      const response = await fetch(`${API_BASE}/status`, {
        method: "GET",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      liveState.online = true;
      liveState.camera = Boolean(data.camera);
      liveState.people = Number(data.people_count || 0);
      liveState.objects = Number(data.object_count || 0);
      liveState.fps = Number(data.fps || 0);
      liveState.uptime = Number(data.uptime || 0);

      updateLiveTelemetry();

      return data;
    } catch (error) {
      liveState.online = false;
      liveState.camera = false;

      updateLiveTelemetry();

      return null;
    }
  }

  function updateLiveTelemetry() {
    const people = document.getElementById("aurex-people-count");
    const objects = document.getElementById("aurex-object-count");
    const fps = document.getElementById("aurex-fps-value");
    const fpsTop = document.getElementById("aurex-live-fps");
    const camera = document.getElementById("aurex-camera-state");
    const uptime = document.getElementById("aurex-runtime-uptime");

    if (people) {
      people.textContent = liveState.people;
    }

    if (objects) {
      objects.textContent = liveState.objects;
    }

    if (fps) {
      fps.textContent = liveState.fps.toFixed(1);
    }

    if (fpsTop) {
      fpsTop.textContent = `${liveState.fps.toFixed(1)} FPS`;
    }

    if (camera) {
      camera.textContent = liveState.camera ? "LIVE" : "OFFLINE";
    }

    if (uptime) {
      uptime.textContent = `Runtime ${Math.floor(liveState.uptime)}s`;
    }

    updateExistingDashboardMetrics();
  }

  function updateExistingDashboardMetrics() {
    const metricValues = document.querySelectorAll(
      ".stage-metric .metric-value",
    );

    if (metricValues.length >= 3) {
      metricValues[0].textContent = liveState.people;

      metricValues[1].textContent = liveState.objects;

      metricValues[2].textContent = liveState.fps.toFixed(0);
    }

    const peopleContext = document.getElementById("context-people");

    if (peopleContext) {
      peopleContext.textContent = `${liveState.people} detected`;
    }
  }

  async function connectBackend() {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: "GET",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      return true;
    } catch {
      return false;
    }
  }

  function refreshCameraModule() {
    if (!moduleIsOpen()) return;

    if (!shouldShowCamera()) return;

    createLivePanel();
    updateLiveTelemetry();
  }

  function observeModuleChanges() {
    const observer = new MutationObserver(() => {
      window.requestAnimationFrame(refreshCameraModule);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class", "style"],
    });
  }

  function bindModuleButtons() {
    document.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest(
          "[data-open-module], .rail-item, .intelligence-card, .quick-action",
        );

        if (!button) return;

        window.setTimeout(refreshCameraModule, 120);

        window.setTimeout(refreshCameraModule, 400);
      },
      true,
    );
  }

  function startTelemetry() {
    if (livePollTimer) {
      clearInterval(livePollTimer);
    }

    fetchRuntimeStatus();

    livePollTimer = setInterval(fetchRuntimeStatus, 700);
  }

  function preloadCameraConnection() {
    const image = new Image();

    image.onload = () => {
      cameraOnline = true;
    };

    image.onerror = () => {
      cameraOnline = false;
    };

    image.src = `${CAMERA_STREAM}?t=${Date.now()}`;
  }

  async function initializeAUREXLiveIntegration() {
    installLivePanelStyles();

    const backend = await connectBackend();

    if (backend) {
      console.log(
        "%cAUREX BACKEND CONNECTED",
        "color:#55e6a5;font-weight:bold;",
      );

      startTelemetry();
      preloadCameraConnection();
    } else {
      console.warn(
        "AUREX backend is not reachable. Start FastAPI on port 8000.",
      );
    }

    observeModuleChanges();
    bindModuleButtons();

    window.setTimeout(refreshCameraModule, 800);
  }

  window.addEventListener("beforeunload", () => {
    if (livePollTimer) {
      clearInterval(livePollTimer);
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      initializeAUREXLiveIntegration,
      { once: true },
    );
  } else {
    initializeAUREXLiveIntegration();
  }

  window.AUREXLive = {
    state: liveState,
    refresh: fetchRuntimeStatus,
    openCamera: refreshCameraModule,
  };
})();
/* ============================================================
   AUREX CAMERA CONTROL
   Global ON / OFF control for the physical camera
   ============================================================ */

(() => {
  "use strict";

  let aurexCameraEnabled = false;
  let aurexCameraStreamElement = null;

  function getCameraFeed() {
    return document.getElementById("aurex-camera-feed");
  }

  function getCameraStatusElement() {
    return document.getElementById("aurex-camera-state");
  }

  function getLiveStatusElement() {
    return document.getElementById("aurex-live-status");
  }

  function getCameraMessage() {
    return document.getElementById("aurex-camera-message");
  }

  function updateCameraUI(enabled) {
    aurexCameraEnabled = enabled;

    const state = getCameraStatusElement();
    const status = getLiveStatusElement();
    const message = getCameraMessage();

    if (state) {
      state.textContent = enabled ? "LIVE" : "OFFLINE";
    }

    if (status) {
      status.classList.toggle("online", enabled);

      status.innerHTML = `
                <span class="aurex-status-dot"></span>
                ${enabled ? "LIVE" : "OFFLINE"}
            `;
    }

    if (message) {
      message.textContent = enabled ? "LIVE PERCEPTION ACTIVE" : "CAMERA OFF";
      message.style.opacity = "1";
    }

    updateCameraButton();
  }

  function updateCameraButton() {
    let button = document.getElementById("aurex-camera-toggle");

    if (!button) return;

    button.textContent = aurexCameraEnabled ? "CAMERA OFF" : "CAMERA ON";

    button.classList.toggle("camera-active", aurexCameraEnabled);
  }

  function createCameraButton() {
    if (document.getElementById("aurex-camera-toggle")) {
      return;
    }

    const panel = document.getElementById("aurex-live-panel");

    if (!panel) return;

    const footer = panel.querySelector(".aurex-live-footer");

    if (!footer) return;

    const button = document.createElement("button");

    button.id = "aurex-camera-toggle";
    button.type = "button";
    button.textContent = "CAMERA ON";

    button.addEventListener("click", async () => {
      if (aurexCameraEnabled) {
        await turnCameraOff();
      } else {
        await turnCameraOn();
      }
    });

    footer.appendChild(button);

    installCameraButtonStyles();

    updateCameraButton();
  }

  async function turnCameraOn() {
    const feed = getCameraFeed();

    if (!feed) {
      console.warn("AUREX camera feed element was not found.");
      return;
    }

    const message = getCameraMessage();

    if (message) {
      message.textContent = "STARTING CAMERA...";
      message.style.opacity = "1";
    }

    try {
      const response = await fetch("/api/camera/start", {
        method: "POST",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`Camera start failed: HTTP ${response.status}`);
      }

      feed.src = `/api/camera/stream?t=${Date.now()}`;

      aurexCameraStreamElement = feed;

      updateCameraUI(true);

      console.log("%cAUREX CAMERA ON", "color:#55e6a5;font-weight:bold;");
    } catch (error) {
      console.error("AUREX camera start error:", error);

      updateCameraUI(false);

      if (message) {
        message.textContent = "CAMERA START FAILED";
        message.style.opacity = "1";
      }
    }
  }

  async function turnCameraOff() {
    const feed = getCameraFeed();

    const message = getCameraMessage();

    if (message) {
      message.textContent = "STOPPING CAMERA...";
      message.style.opacity = "1";
    }

    /*
     * Stop the browser-side stream immediately.
     */
    if (feed) {
      feed.removeAttribute("src");
    }

    aurexCameraStreamElement = null;

    /*
     * Tell FastAPI to release the physical camera.
     */
    try {
      await fetch("/api/camera/stop", {
        method: "POST",
        cache: "no-store",
      });
    } catch (error) {
      console.warn("AUREX camera stop request failed:", error);
    }

    updateCameraUI(false);

    console.log("%cAUREX CAMERA OFF", "color:#ff8585;font-weight:bold;");
  }

  function installCameraButtonStyles() {
    if (document.getElementById("aurex-camera-button-styles")) {
      return;
    }

    const style = document.createElement("style");

    style.id = "aurex-camera-button-styles";

    style.textContent = `
            #aurex-camera-toggle {
                margin-left: auto;
                padding: 9px 14px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,.14);
                background: rgba(255,255,255,.055);
                color: rgba(235,242,250,.82);
                font-family: inherit;
                font-size: 9px;
                font-weight: 600;
                letter-spacing: .14em;
                cursor: pointer;
                transition:
                    transform .2s ease,
                    background .2s ease,
                    border-color .2s ease,
                    box-shadow .2s ease;
            }

            #aurex-camera-toggle:hover {
                transform: translateY(-1px);
                background: rgba(255,255,255,.09);
                border-color: rgba(150,210,255,.4);
            }

            #aurex-camera-toggle.camera-active {
                border-color: rgba(85,230,165,.35);
                background: rgba(85,230,165,.08);
                color: rgba(170,255,215,.92);
                box-shadow:
                    0 0 18px rgba(85,230,165,.08);
            }

            #aurex-camera-toggle.camera-active:hover {
                border-color: rgba(255,110,110,.45);
                background: rgba(255,110,110,.08);
                color: rgba(255,190,190,.95);
            }

            @media (max-width: 600px) {
                #aurex-camera-toggle {
                    margin-left: 0;
                }
            }
        `;

    document.head.appendChild(style);
  }

  function watchForLivePanel() {
    const observer = new MutationObserver(() => {
      const panel = document.getElementById("aurex-live-panel");

      if (panel) {
        createCameraButton();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    createCameraButton();
  }

  /*
   * Make controls available globally.
   */
  window.AUREXCameraControl = {
    on: turnCameraOn,
    off: turnCameraOff,
    toggle: async () => {
      if (aurexCameraEnabled) {
        await turnCameraOff();
      } else {
        await turnCameraOn();
      }
    },
    status: () => aurexCameraEnabled,
  };

  /*
   * Start watching the AUREX UI.
   */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watchForLivePanel, {
      once: true,
    });
  } else {
    watchForLivePanel();
  }
})();

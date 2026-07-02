# Robotic Inspection Simulator

[![CI](https://github.com/earosenfeld/robotic-inspection-system/actions/workflows/ci.yml/badge.svg)](https://github.com/earosenfeld/robotic-inspection-system/actions/workflows/ci.yml)

A Python simulator for a robotic inspection cell: a 6-DOF arm (DH-parameter
forward/inverse kinematics, per-joint PID servo stepping), a simulated
inspection camera, a latched safety system (light curtain, door switch,
e-stop), and a Streamlit GUI to drive it all.

## What's real vs simulated

| Component | Status |
|---|---|
| Kinematics (`app/models/robotic_arm.py`) | Real math — DH forward kinematics, iterative inverse kinematics, joint limits |
| Joint motion (`step_towards`) | Real control loop — per-joint PID velocity commands with anti-windup, integrated over explicit timesteps |
| Safety system (`app/models/safety_system.py`) | Simulated but faithful — latched faults, RESET_REQUIRED acknowledge cycle like an industrial safety relay |
| Camera / inspection results | Simulated — synthetic pass/fail data, no real image processing |
| Hardware I/O | None — everything runs in-process |

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulator (the GUI is a Streamlit app):
```bash
streamlit run app/views/gui.py
# or equivalently:
python scripts/run_simulation.py
```

## Project structure

```
robotic-inspection-system/
├── app/
│   ├── controllers/
│   │   ├── robotic_arm_controller.py
│   │   ├── camera_controller.py
│   │   └── safety_controller.py
│   ├── models/
│   │   ├── robotic_arm.py       # DH kinematics, IK, PID-driven joint stepping
│   │   ├── pid_controller.py    # PID with explicit-dt mode and anti-windup
│   │   ├── camera.py
│   │   └── safety_system.py     # latched safety state machine
│   ├── services/
│   │   └── inspection_service.py
│   ├── views/
│   │   └── gui.py               # Streamlit GUI
│   ├── config/
│   │   └── camera_config.py
│   └── utils/
│       └── visualization.py
├── data/
│   └── configs/
│       └── parts_inspection_config.json
├── scripts/
│   ├── run_simulation.py        # wraps `streamlit run`
│   └── test_inspection.py
├── tests/
│   ├── test_robotic_arm.py
│   ├── test_pid_controller.py
│   └── test_safety_system.py
└── requirements.txt
```

## Usage

1. Launch the GUI with `streamlit run app/views/gui.py`
2. Select a part type to inspect
3. Configure inspection parameters if needed
4. Start the simulation and monitor the inspection process
5. Trigger safety events (light curtain, door, e-stop) and observe the
   latched fault → clear → reset-required → reset cycle

## Safety model

The safety system mirrors industrial behavior: any fault (e-stop, light
curtain break, door open) latches the system out of NORMAL. Clearing the
fault moves it to RESET_REQUIRED — motion stays inhibited until an explicit
system reset acknowledges the event. Every transition is logged with a
timestamped event history.

## Development

```bash
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE).

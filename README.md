# Robotic Inspection Simulator

A Python-based simulator for a robotic inspection cell that mimics industrial system behavior with simulated sensors, actuators, and camera data.

## Features

- 6-DOF robotic arm simulation with PID control
- Forward and inverse kinematics
- Simulated camera system for part inspection
- Safety system simulation (light curtain, door switches)
- Interactive GUI for operation control
- Configurable part inspection sequences

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulator:
```bash
python scripts/run_simulation.py
```

## Project Structure

- `app/`: Main application code
  - `controllers/`: Control logic for robot, camera, and safety systems
  - `models/`: Core simulation models
  - `services/`: Business logic and inspection services
  - `views/`: GUI components
  - `utils/`: Utility functions and helpers
- `data/`: Configuration and simulated image data
- `scripts/`: Execution scripts
- `tests/`: Unit tests

## Usage

1. Launch the application using the run script
2. Select a part type to inspect from the GUI
3. Configure inspection parameters if needed
4. Start the simulation
5. Monitor the inspection process
6. View results and logs

## Safety Features

- Emergency stop functionality
- Light curtain simulation
- Door switch monitoring
- Automatic system halt on safety events

## Development

To run tests:
```bash
pytest tests/
```

## License

MIT License

robotic-inspection-simulator/
├── app/
│   ├── controllers/
│   │   ├── robotic_arm_controller.py
│   │   ├── camera_controller.py
│   │   └── safety_controller.py
│   ├── models/
│   │   ├── robotic_arm.py  # includes 6-DOF joint simulation
│   │   ├── pid_controller.py
│   │   ├── camera.py
│   │   └── inspection_part.py
│   ├── services/
│   │   ├── inspection_service.py
│   │   └── simulation_service.py
│   ├── views/
│   │   ├── gui.py
│   │   └── components/
│   │       └── inspection_selector.py
│   └── utils/
│       ├── constants.py
│       ├── config_loader.py
│       └── logger.py
├── data/
│   ├── configs/
│   │   └── parts_inspection_config.json
│   └── images/
│       └── simulated/
│           └── part_X_scene_1.png
├── scripts/
│   └── run_simulation.py
├── tests/
│   └── test_*.py
├── requirements.txt
├── setup.py
└── README.md
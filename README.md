# 🤖 Robotic Inspection System - Interactive Simulation

A modern robotic inspection system simulation that combines real-time arm control with smooth animation and scene-based inspection workflows. Perfect for learning robotic programming concepts and testing inspection sequences.

## 🚀 Quick Start

### Run the Simulation
```bash
# Navigate to the project directory
cd robotic-inspection-system

# Run the simulation
streamlit run scripts/run_simulation.py
```

The simulation will open in your browser at `http://localhost:8501`

## 🎯 How It Works

### **Interactive Arm Control**
- **Real-time Sliders**: Drag the 6 joint sliders to move the robotic arm instantly
- **3D Visualization**: See the arm move in real-time as you control it
- **Click-to-Move**: Click on the 3D visualization to move the arm to specific positions
- **Preset Positions**: Quick buttons for common inspection angles (Home, Top View, Front View, Side View)

### **Teach-by-Touch Programming**
1. **Move the Arm**: Use sliders or click the 3D visualization to position the arm
2. **Configure Settings**: Set inspection type, view, lighting, and camera settings
3. **Record Poses**: Click "📸 Record Current Pose" to save the position
4. **Create Scenes**: Build inspection sequences from multiple recorded poses
5. **Test Animation**: Watch the arm move smoothly through all recorded poses

### **Smooth Animation System**
- **Fluid Motion**: The arm moves smoothly between recorded poses using inverse kinematics
- **8 Interpolation Steps**: Between each recorded pose for realistic motion
- **IK-Based Path Planning**: Optimal joint angles calculated for each position
- **Progress Tracking**: See both interpolated steps and original pose numbers
- **Multiple Controls**: Step-by-step, play all, pause, or restart animation

## 🎮 Interactive Features

### **Real-Time Controls**
- **6-DOF Sliders**: Individual control for each joint (Base, Shoulder, Elbow, Wrist 1/2/3)
- **Immediate Feedback**: Arm moves instantly as you drag sliders
- **3D Click Control**: Click anywhere on the arm visualization to move to that position
- **Camera Controls**: Switch between Front, Side, Top, and Isometric views

### **Scene Configuration**
Each recorded pose can have unique settings:
- **Inspection Types**: surface_quality, scratches_small/large, fingerprints, edge_quality, comprehensive
- **View Types**: top_view, front_view, back_view, side_view, custom_view, angled_view
- **Lighting Options**: standard, diffuse, directional, low_angle, multi_angle, backlight
- **Camera Settings**: default, high_resolution, low_resolution, wide_angle, telephoto

### **Animation Controls**
- **🧪 Test Complete Scene**: Start smooth animation through all recorded poses
- **⏭️ Next Step**: Manually advance through interpolated poses
- **⏸️ Pause Animation**: Stop at any point
- **🔄 Restart Animation**: Start over from the beginning
- **▶️ Play All Smooth**: Automatic smooth playback with timing

## 🏗️ System Architecture

```
app/
├── config/           # Camera and system configuration
├── controllers/      # Hardware controllers (arm, camera, safety)
├── models/          # Data models and PID controllers
├── services/        # Business logic and inspection services
├── utils/           # Visualization and inverse kinematics
└── views/           # Streamlit GUI components
```

## 🎬 Animation Workflow

### **Step 1: Record Poses**
1. Use sliders to move the arm to desired positions
2. Configure inspection settings for each pose
3. Click "📸 Record Current Pose" to save each position

### **Step 2: Test Animation**
1. Click "🧪 Test Complete Scene" to start smooth animation
2. Watch the arm move fluidly through all recorded poses
3. Use controls to pause, step through, or restart

### **Step 3: Create Scenes**
1. Build reusable inspection scenes from recorded poses
2. Save scenes for different parts and inspection types
3. Execute complete inspection sequences

## 🧪 Testing Features

### **Real-Time Testing**
- **Individual Pose Testing**: Test each pose's configuration
- **Scene Testing**: Run complete inspection sequences
- **Configuration Editing**: Modify settings for each pose
- **Visual Feedback**: See results and status updates

### **Animation Features**
- **Smooth Interpolation**: 8 intermediate steps between poses
- **IK-Based Motion**: Optimal joint angles for each position
- **Progress Tracking**: Visual progress bar and step counter
- **Original Pose Mapping**: Shows which original pose you're closest to

## 📊 Recent Improvements

### **Interactive Controls**
- ✅ **Real-time Slider Response**: Arm moves instantly as you drag sliders
- ✅ **3D Click Control**: Click visualization to move arm to specific positions
- ✅ **Immediate Visual Feedback**: See arm movement in real-time
- ✅ **Preset Position Buttons**: Quick access to common inspection angles

### **Smooth Animation**
- ✅ **Fluid Motion**: Smooth interpolation between recorded poses
- ✅ **IK-Based Path Planning**: Inverse kinematics for optimal motion
- ✅ **8 Interpolation Steps**: Realistic motion between poses
- ✅ **Progress Tracking**: Shows both interpolated and original pose numbers
- ✅ **Multiple Control Options**: Step-by-step, play all, pause, restart

### **Layout Improvements**
- ✅ **Three-Column Layout**: Arm visualization, controls, and camera view
- ✅ **Better Space Utilization**: Optimized for simultaneous viewing
- ✅ **Integrated Controls**: Pose recording and testing next to visualization
- ✅ **Wide Layout**: Full-width page for better user experience

## 🔧 Technical Details

### **Dependencies**
- **Streamlit**: Modern web interface
- **Plotly**: 3D visualization and interactive plots
- **NumPy**: Numerical computations
- **OpenCV**: Image processing and camera simulation
- **SciPy**: Inverse kinematics calculations

### **Key Algorithms**
- **Inverse Kinematics**: Calculates optimal joint angles for target positions
- **Pose Interpolation**: Smooth motion between recorded poses
- **Real-time Visualization**: Live 3D arm representation
- **Scene Management**: Configuration and execution of inspection sequences

## 🎯 Use Cases

### **Learning & Training**
- **Robotic Programming**: Learn joint control and inverse kinematics
- **Inspection Workflows**: Practice creating inspection sequences
- **Animation Concepts**: Understand smooth motion planning

### **Testing & Development**
- **Inspection Sequences**: Test and validate inspection procedures
- **Motion Planning**: Verify reachability and collision avoidance
- **Configuration Testing**: Test different inspection parameters

### **Demonstration**
- **Visual Presentations**: Show inspection procedures with smooth animation
- **Training Materials**: Create visual guides for inspection processes
- **Documentation**: Generate visual records of inspection sequences

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Simulation**:
   ```bash
   streamlit run scripts/run_simulation.py
   ```

3. **Start Exploring**:
   - Move the arm using sliders
   - Record poses with different configurations
   - Test smooth animation between poses
   - Create and save inspection scenes

## 🎉 Key Features Summary

- **🎮 Real-time Control**: Instant arm movement with sliders and 3D clicks
- **🎬 Smooth Animation**: Fluid motion through recorded poses using IK
- **📸 Pose Recording**: Save positions with custom inspection settings
- **🎯 Scene Creation**: Build reusable inspection sequences
- **📊 Visual Feedback**: Real-time 3D visualization and progress tracking
- **⚡ Quick Presets**: Common inspection positions at the click of a button

The system provides an intuitive way to learn robotic programming concepts while creating realistic inspection workflows with smooth, professional animations.
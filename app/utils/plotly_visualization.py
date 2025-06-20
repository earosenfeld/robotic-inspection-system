import plotly.graph_objects as go

class PlotlyArmVisualizer:
    """Plotly-based 3-D visualizer for the robotic arm (smooth WebGL rendering)."""

    def __init__(self):
        self.fig = go.Figure()
        self._initialised = False

    def plot_arm(self, joint_positions):
        """Create or update the arm scatter/line trace.

        Args:
            joint_positions: List of [x, y, z] coordinates for each joint (including base).
        Returns:
            plotly.graph_objects.Figure: Updated figure to display.
        """
        # Unpack coordinates
        x, y, z = list(zip(*joint_positions))  # tuple of tuples ➜ lists

        if not self._initialised:
            # First time: build figure & trace
            self.fig.add_trace(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="markers+lines",
                    marker=dict(size=5, color="crimson"),
                    line=dict(width=6, color="royalblue"),
                )
            )
            self.fig.update_layout(
                scene=dict(
                    xaxis=dict(range=[-1, 1], autorange=False),
                    yaxis=dict(range=[-1, 1], autorange=False),
                    zaxis=dict(range=[0, 1], autorange=False),
                    aspectmode="cube",
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                margin=dict(l=0, r=0, b=0, t=0),
                showlegend=False,
                # Disable default camera controls
                dragmode=False,
                hovermode=False,
            )
            # Disable camera controls on the scene
            self.fig.update_scenes(
                dragmode=False,
                hovermode=False,
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            )
            self._initialised = True
        else:
            # Update existing trace for smoother animation
            trace = self.fig.data[0]
            trace.x = x
            trace.y = y
            trace.z = z

        return self.fig 
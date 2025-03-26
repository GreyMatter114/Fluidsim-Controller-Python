# import serial
import numpy as np
from matplotlib import animation
import matplotlib.pyplot as plt
import threading
from pythonsph.config import Config
# import pythonsph.ports as ports
import hidgamepad.asynchronous
from pythonsph.particle import Particle
from pythonsph.physics import (
    start,
    calculate_density,
    create_pressure,
    calculate_viscosity,
)

# Setting up the accelerometer connection (replace with your specific port)
# ser = serial.Serial(ports.port, 9600, timeout=1)  # Adjust COM_PORT as per your setup

# Shared variables for simulation state
gravity_x = 0.0
gravity_y = 0.0
simulation_active = True
serial_reading_active = False
simulation_state = []
dam_built = False

# Simulation setup
(
    N,
    SIM_W,
    BOTTOM,
    DAM,
    DAM_BREAK,
    G,
    SPACING,
    K,
    K_NEAR,
    REST_DENSITY,
    R,
    SIGMA,
    MAX_VEL,
    WALL_DAMP,
    VEL_DAMP,
) = Config().return_config()

# Read accelerometer data (in a separate thread)
def read_accelerometer_data():
    global gravity_x, gravity_y, serial_reading_active
    try:
        while True:
            try:
                data = ser.readline().decode('utf-8').strip()
            except:
                print(f"Error Reading from Device at {ports.port}, exiting...")
                sys.exit()
            if data:
                if "START" in data:
                    serial_reading_active = True
                    print("Started reading accelerometer data.")
                elif "E" in data:
                    serial_reading_active = False
                    print("Stopped reading accelerometer data.")
                elif "," in data and serial_reading_active:
                    x_accel, y_accel, z_accel = map(float, data.split(','))
                    gravity_x = -x_accel  # Use this value to modify simulation's X gravity
                    gravity_y = -y_accel  # Use this value to modify simulation's Y gravity
                else:
                    print("Invalid Data")
    except Exception as e:
        print(f"Error reading accelerometer data: {e}")

# Update simulation (in a separate thread)
def update_simulation():
    global simulation_state, dam_built
    while True:
        if simulation_active:
            # Apply accelerometer data as external forces
            for particle in simulation_state:
                particle.x_vel += gravity_x * 0.003  # Scale factor to prevent excessive movement
                particle.y_vel += gravity_y * 0.005

            # Update particle states and simulation steps
            for particle in simulation_state:
                particle.update_state(dam_built)

            calculate_density(simulation_state)

            for particle in simulation_state:
                particle.calculate_pressure()

            create_pressure(simulation_state)
            calculate_viscosity(simulation_state)
        
        threading.Event().wait(0.01)  # Sleep to prevent high CPU usage

# Animation update (runs in the main thread)
def animate(i: int):
    global simulation_state
    # , dam_built
    # if i == 250:  # Break the dam at frame 250
    #     print("Breaking the dam")
    #     dam_built = False

    # Create an array with the x and y coordinates of the particles
    visual = np.array(
        [
            [particle.visual_x_pos, particle.visual_y_pos]
            for particle in simulation_state
        ]
    )
    POINTS.set_data(visual[:, 0], visual[:, 1])  # Update the position of the particles
    return (POINTS,)

# Handle key press events (runs in a separate thread)
def on_key(event):
    global simulation_active, serial_reading_active
    if event.key == 'p':
        simulation_active = not simulation_active
        if simulation_active:
            print("Simulation Resumed")
        else:
            print("Simulation Paused")
    elif event.key == 'q':
        print("Exiting simulation...")
        plt.close()
    elif event.key == 's':  # Start accelerometer data reading
        serial_reading_active = True
        print("Started reading accelerometer data.")
    elif event.key == 't':  # Stop accelerometer data reading
        serial_reading_active = False
        print("Stopped reading accelerometer data.")

# Setup matplotlib
fig = plt.figure()
axes = fig.add_subplot(xlim=(-SIM_W, SIM_W), ylim=(0, SIM_W))
(POINTS,) = axes.plot([], [], "bo", ms=20)

simulation_state = start(-SIM_W, DAM, BOTTOM, 0.03, N)

# Connect key press events to the figure
fig.canvas.mpl_connect('key_press_event', on_key)

# Start threads
accel_thread = threading.Thread(target=read_gamepad_data, daemon=True)
simulation_thread = threading.Thread(target=update_simulation, daemon=True)

accel_thread.start()
simulation_thread.start()

# Animation function
ani = animation.FuncAnimation(fig, animate, interval=10, blit=True)
plt.show()

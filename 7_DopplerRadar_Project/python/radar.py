import serial
import pygame
import math
import threading
import time


# SETTINGS
SERIAL_PORT = "COM5"
BAUD_RATE = 9600

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

MAX_DISTANCE = 40.0

RADAR_RADIUS = 300

# GLOBAL DATA
current_angle = 0.0
current_distance = -1.0

# Minimum distance change between neighboring readings
# to consider it an edge of a target.
DISTANCE_GAP_THRESHOLD = 25.0

# Minimum number of readings required to form a target.
MIN_TARGET_READINGS = 3

# Size of the target blip in pixels
TARGET_THICKNESS = 8

points = []

data_lock = threading.Lock()

running = True

center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2

#for background subtraction
background = {}

BACKGROUND_THRESHOLD = 20.0
background_complete = False

def serial_reader():

    global current_angle
    global current_distance
    global background_complete

    try:

        serial_port = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )

        print(f"Connected to {SERIAL_PORT}")

        time.sleep(2)

        while running:

            line = serial_port.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            # -------------------------------------------------
            # BACKGROUND READING
            # -------------------------------------------------

            if line.startswith("BG,"):

                parts = line.split(",")

                if len(parts) != 3:
                    continue

                try:

                    step = int(parts[1])
                    distance = float(parts[2])

                    background[step] = distance

                except ValueError:
                    continue

                continue

            # -------------------------------------------------
            # BACKGROUND COMPLETE
            # -------------------------------------------------

            if line == "BG_END":

                background_complete = True

                print(
                    f"Background map complete: "
                    f"{len(background)} readings"
                )

                continue

            # -------------------------------------------------
            # NORMAL RADAR READING
            # -------------------------------------------------

            try:

                parts = line.split(",")

                if len(parts) != 2:
                    continue

                angle = float(parts[0])
                distance = float(parts[1])

                with data_lock:

                    current_angle = angle
                    current_distance = distance

                    # -----------------------------------------
                    # Ignore background terrain
                    # -----------------------------------------

                    if background_complete and distance >= 0:

                        step = round(
                            angle / 1.8
                        )

                        background_distance = background.get(
                            step,
                            -1
                        )

                        if background_distance >= 0:

                            difference = abs(
                                distance - background_distance
                            )

                            # Same as background → ignore
                            if difference < BACKGROUND_THRESHOLD:
                                continue

                    # -----------------------------------------
                    # This is potentially a target
                    # -----------------------------------------

                    if distance >= 0:

                        points.append(
                            (angle, distance)
                        )

                        if len(points) > 500:
                            points.pop(0)

            except ValueError:
                continue

        serial_port.close()

    except serial.SerialException as error:

        print("Serial connection failed:")
        print(error)

# # SERIAL READER
# def serial_reader():

#     global current_angle
#     global current_distance

#     try:

#         serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

#         print(f"Connected to {SERIAL_PORT}")

#         time.sleep(2)

#         while running:

#             line = serial_port.readline().decode("utf-8", errors="ignore").strip()

#             if not line:
#                 continue

#             try:

#                 parts = line.split(",")

#                 if len(parts) != 2:
#                     continue

#                 angle = float(parts[0])
#                 distance = float(parts[1])

#                 with data_lock:

#                     current_angle = angle
#                     current_distance = distance

#                     if distance >= 0:
#                         points.append((angle, distance))

#                         # Keep the list from growing forever
#                         if len(points) > 500:
#                             points.pop(0)

#             except ValueError:
#                 continue

#         serial_port.close()

#     except serial.SerialException as error:

#         print("Serial connection failed:")
#         print(error)


# POLAR → SCREEN COORDINATES
def polar_to_screen(angle, distance):

    # Convert distance to pixels
    radius = (distance / MAX_DISTANCE * RADAR_RADIUS)

    # Convert angle to radians
    radians = math.radians(angle)

    x = center_x + radius * math.cos(radians)

    y = center_y - radius * math.sin(radians)

    return int(x), int(y)


# DRAW RADAR
def draw_radar(screen):

    font = pygame.font.SysFont("Arial", 12)

    # Radar arcs (% based)
    for distance in [0.25, 0.50, 0.75, 1.0]:

        radius = distance * RADAR_RADIUS
        distance_val = int(MAX_DISTANCE * distance)

        rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)

        pygame.draw.arc(screen, (0, 180, 0), rect, 0, math.pi * 2, 2)

        # Render Text Label
        label = font.render(str(distance_val), True, (0, 255, 0))
        label_rect = label.get_rect()
        label_rect.top = center_y + 5

        # Right intersection
        label_rect.centerx = center_x + radius
        screen.blit(label, label_rect)

        # Left intersection
        label_rect.centerx = center_x - radius
        screen.blit(label, label_rect)

    # Horizontal line
    pygame.draw.line(screen, (0, 180, 0), (center_x - RADAR_RADIUS, center_y), (center_x + RADAR_RADIUS, center_y), 2)

    # Angle lines | am i getting inverted positions?
    for angle in [30, 60, 90, 120, 150, 210, 240, 270, 300, 330]:

        radians = math.radians(angle)

        x = (center_x + RADAR_RADIUS * math.cos(radians))

        y = (center_y - RADAR_RADIUS * math.sin(radians))

        pygame.draw.line(screen, (0, 180, 0), (center_x, center_y), (x, y), 2)


# DRAW DETECTED POINTS
def draw_points(screen):

    with data_lock:
        current_points = points.copy()

    if len(current_points) < 2:
        return

    # ---------------------------------------------------------
    # Find contiguous target regions
    # ---------------------------------------------------------

    targets = []

    current_target = []

    for i in range(len(current_points)):

        angle, distance = current_points[i]

        # Ignore invalid / out-of-range measurements
        if distance < 0 or distance > MAX_DISTANCE:
            continue

        # First valid reading
        if not current_target:
            current_target.append((angle, distance))
            continue

        previous_angle, previous_distance = current_target[-1]

        # Difference between this reading and previous reading
        distance_difference = abs(distance - previous_distance)

        # Make sure the readings are actually next to each other
        angle_difference = abs(angle - previous_angle)

        if (
            distance_difference <= DISTANCE_GAP_THRESHOLD
            and angle_difference <= 2.0
        ):

            # Same contiguous region
            current_target.append((angle, distance))

        else:

            # Current region has ended
            if len(current_target) >= MIN_TARGET_READINGS:
                targets.append(current_target)

            # Start a new region
            current_target = [(angle, distance)]

    # Don't forget the final region
    if len(current_target) >= MIN_TARGET_READINGS:
        targets.append(current_target)

    # ---------------------------------------------------------
    # Draw each target as one circular blip
    # ---------------------------------------------------------

    for target in targets:

        # First and last readings of the contiguous region
        first_angle, first_distance = target[0]
        last_angle, last_distance = target[-1]

        # -----------------------------------------------------
        # Calculate average distance of the target
        # -----------------------------------------------------

        average_distance = sum(
            distance for angle, distance in target
        ) / len(target)

        # -----------------------------------------------------
        # Convert first and last edges to screen coordinates
        # -----------------------------------------------------

        x1, y1 = polar_to_screen(
            first_angle,
            average_distance
        )

        x2, y2 = polar_to_screen(
            last_angle,
            average_distance
        )

        # -----------------------------------------------------
        # Distance between the two edges
        #
        # This becomes the diameter of the blip.
        # -----------------------------------------------------

        edge_distance = math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )

        # Convert diameter to radius
        radius = max(3, int(edge_distance / 2))

        # -----------------------------------------------------
        # Center of the target
        # -----------------------------------------------------

        middle_angle = (
            first_angle + last_angle
        ) / 2

        center_x_target, center_y_target = polar_to_screen(
            middle_angle,
            average_distance
        )

        # -----------------------------------------------------
        # Draw the blip
        # -----------------------------------------------------

        pygame.draw.circle(
            screen,
            (255, 50, 50),
            (center_x_target, center_y_target),
            radius
        )


# DRAW SWEEP LINE
def draw_sweep(screen, angle):

    radians = math.radians(angle)

    x = (center_x + RADAR_RADIUS * math.cos(radians))

    y = (center_y - RADAR_RADIUS * math.sin(radians))

    pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (x, y), 3)



# DRAW INFORMATION
def draw_text(screen, font):

    with data_lock:

        angle = current_angle
        distance = current_distance

    angle_text = f"Angle: {angle:.1f}°"

    if distance >= 0:
        distance_text = f"Distance: {distance:.1f} cm"
    else:
        distance_text = "Distance: No Echo"

    screen.blit(font.render(angle_text, True, (0, 255, 0)), (30, 30))

    screen.blit(font.render(distance_text, True, (0, 255, 0)), (30, 65))


# MAIN
def main():

    global running

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Ultrasonic NEMA 17 Radar")

    font = pygame.font.SysFont("Arial",28)

    clock = pygame.time.Clock()

    # Start serial thread
    thread = threading.Thread(target=serial_reader, daemon=True)

    thread.start()

    while running:

        # Handle events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

        # Background
        screen.fill((0, 0, 0))

        # Radar
        draw_radar(screen)
        draw_points(screen)

        with data_lock:
            angle = current_angle

        draw_sweep(screen, angle)

        draw_text(screen, font)

        # ----------------------------------------------------
        # Update screen
        # ----------------------------------------------------

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


# START
if __name__ == "__main__":
    main()
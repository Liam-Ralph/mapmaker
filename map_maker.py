# Imports
import ctypes
import multiprocessing
import multiprocessing.managers
import os
import PIL.Image
import random
import scipy
import time
import traceback


# Classes

class Dot:
    def __init__(self, x, y, dot_type):
        self.x = x
        self.y = y
        self.type = dot_type

class TreeManager(multiprocessing.managers.BaseManager):
    pass

# Text Colors

ANSI_GREEN = "\u001b[38;5;2m"
ANSI_BLUE = "\u001b[38;5;4m"
ANSI_RESET = "\u001b[0m"


# Functions
# (Alphabetical order)

def format_time(time_seconds):
    seconds = "{:.2f}".format(time_seconds % 60).rjust(5, "0")
    minutes = str(int(time_seconds // 60))
    return (minutes + ":" + seconds).rjust(8)

def get_int(min, max):

    while True:

        choice = input()

        try:
            choice = int(choice)
        except ValueError:
            print("Input must be a whole number.")
            continue

        if min <= choice <= max:
            break
        else:
            print("Input must be between", min, "and", max, "(both inclusive).")

    return choice

def raise_error(location, traceback_output, notes = None):
    with open("errors.txt", "a") as file:
        file.write("Error at " + location + "\n" + traceback_output + "\n")
        if notes != None:
            for note in notes:
                file.write(note, "\n")
        file.write("\n")


# Multiprocessing Functions
# (Order of use)

def initialize_pool(progress_value, dots_value, width_value, height_value, processes_value,
start_time_value, section_times_value, tree_value,
island_abundance_value, island_size_value, relative_island_abundance_value,
pixels_value, current_section_progress_value):
    
    global progress
    global dots
    global width
    global height
    global processes
    global start_time
    global section_times
    global tree
    global island_abundance
    global island_size
    global relative_island_abundance
    global pixels
    global current_section_progress

    progress = progress_value
    dots = dots_value
    width = width_value
    height = height_value
    processes = processes_value
    start_time = start_time_value
    section_times = section_times_value
    tree = tree_value
    island_abundance = island_abundance_value
    island_size = island_size_value
    relative_island_abundance = relative_island_abundance_value
    pixels = pixels_value
    current_section_progress = current_section_progress_value

def generate_sections(coord, total):

    try:

        dot_type = "Water"
        if random.randint(1, relative_island_abundance.value) == 1:
            dot_type = "Land Origin"
        elif random.randint(1, (relative_island_abundance.value - 1)) == 1:
            dot_type = "Water Forced"
        dots.append(Dot(coord % width.value, coord // width.value, dot_type))

        progress[0] += 1
        progress_section_generation = progress[0] / total * 100
        current_section_progress.value = progress_section_generation
        
        color = ANSI_BLUE
        if progress_section_generation == 100.0:
            color = ANSI_GREEN
        complete_bars = round(progress[0] / total * 20)
        print(
            "\033[A" +
            color + "[1/4] " + ANSI_RESET + "Section Generation  " + color +
            ("{:.2f}".format(progress_section_generation) + "%").rjust(7) + " " +
            ANSI_GREEN + "█" * complete_bars +
            ANSI_BLUE + "█" * (20 - complete_bars) +
            ANSI_RESET + " " + format_time(time.time() - start_time.value)
        )

    except:
        raise_error(
            "generate_sections", traceback.format_exc(), notes = ("Input: " + str(coord), )
        )

def generate_image(x, y, total):

    try:

        pixel_type = "Error"
        pixel_type = dots[tree.query([(x, y)])[1][0]].type

        match (pixel_type):
            case "Land":
                pixels[y][x] = (0, 204, 0)
            case "Land Origin":
                pixels[y][x] = (0, 102, 0)
            case "Water":
                pixels[y][x] = (0, 0, 204)
            case "Water Forced":
                pixels[y][x] = (0, 0, 102)
            case "Error":
                pixels[y][x] = (255, 102, 163)
            case _:
                pixels[y][x] = (204, 0, 82)


        progress[1] += 1
        progress_section_generation = progress[1] / total * 100
        current_section_progress.value = progress_section_generation

        color = ANSI_BLUE
        if progress_section_generation == 100.0:
            color = ANSI_GREEN
        complete_bars = round(progress[1] / total * 20)
        print(
            "\033[A" +
            color + "[4/4] " + ANSI_RESET + "Image Generation    " + color +
            ("{:.2f}".format(progress_section_generation) + "%").rjust(7) + " " +
            ANSI_GREEN + "█" * complete_bars +
            ANSI_BLUE + "█" * (20 - complete_bars) +
            ANSI_RESET + " " + format_time(time.time() - start_time.value - section_times[0])
        )

    except:
        raise_error(
            "generate_image", traceback.format_exc(),
            notes = ("Input \"x\": " + str(x), "Input \"y\": " + str(y))
        )


if __name__ == "__main__":

    with open("errors.txt", "w") as file:
        file.write("")

    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)

    print(
        "Welcome to MapMaker v1.0\n" + 
        "\nMap Width:"
    )
    width_input = get_int(100, 10_000)

    print("\nMap Height:")
    height_input = get_int(100, 10_000)

    print(
        "\nIsland abundance controls how many islands are generated.\n" +
        "Choose a number between 50 and 1000. 100 is the default.\n" +
        "Larger numbers produce fewer islands.\n" +
        "Island Abundance:"
    )
    island_abundance_input = get_int(50, 1000)

    print(
        "\nIsland size controls average island size.\n" +
        "Choose a number between 10 and 100. 20 is the default.\n" +
        "Larger numbers produce larger islands.\n" +
        "Island Size:"
    )
    island_size_input = get_int(10, 100)

    print(
        "\nRelative island abundance controls the ratio of land to water.\n" +
        "Choose a number between 10 and 50. 30 is the default.\n" +
        "Larger numbers produces more land.\n" +
        "Relative Island Abundance:"
    )
    relative_island_abundance_input = get_int(10, 100)

    print(
        "\nNow you must choose how many of your CPU's threads to use for map generation.\n" +
        "Values exceeding your CPU's number of threads will slow map generation.\n" +
        "A maximum of four less than your CPU's number of threads is recommended,\n" +
        "to leave threads available for your system's background processes.\n" +
        "Ensure you monitor your CPU for overheating, and halt the program if\n" +
        "high temperatures occur. Using fewer threads may reduce temperatures.\n" +
        "Number of Threads:"
    )
    processes_input = get_int(1, 32)
    if processes_input > 1:
        processes_input -= 1

    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)

    TreeManager.register("Tree", scipy.spatial.KDTree)

    manager = multiprocessing.Manager()
    tree_manager = TreeManager()
    tree_manager.start()

    progress = multiprocessing.Array(ctypes.c_int, [0, 0, 0, 0])
    dots = manager.list([])
    width = multiprocessing.Value(ctypes.c_int, width_input)
    height = multiprocessing.Value(ctypes.c_int, height_input)
    processes = multiprocessing.Value(ctypes.c_int, processes_input)
    start_time = multiprocessing.Value(ctypes.c_double, time.time())
    section_times = multiprocessing.Array(ctypes.c_double, [0.0, 0.0, 0.0, 0.0])
    tree = tree_manager.Tree([(0, 0), (1, 1)])
    island_abundance = multiprocessing.Value(ctypes.c_int, island_abundance_input)
    island_size = multiprocessing.Value(ctypes.c_int, island_size_input)
    relative_island_abundance = multiprocessing.Value(ctypes.c_int, relative_island_abundance_input)
    pixels = manager.list([[(255, 0, 102)] * width.value] * height.value)
    current_section_progress = multiprocessing.Value(ctypes.c_double, 0.0)

    with multiprocessing.Pool(processes_input, initializer = initialize_pool, initargs =
    (progress, dots, width, height, processes, start_time, section_times, tree, island_abundance, island_size, relative_island_abundance, pixels, current_section_progress)) as pool:

        try:

            # Section Generation

            print(
                ANSI_BLUE + "[1/4] " + ANSI_RESET + "Section Generation  " +
                "  0.00% " + ANSI_BLUE + "█" * 20 + ANSI_RESET
            )

            num_dots = width.value * height.value // island_abundance.value
            results = []
            for coord in random.sample(range(0, width.value * height.value), num_dots):
                results.append(pool.apply_async(generate_sections, (coord, num_dots)))
            [result.wait() for result in results]

            dot_coords = []
            for dot in dots:
                dot_coords.append((dot.x, dot.y))
            tree.data = dot_coords

            time_now = time.time()
            section_times[0] = time_now - start_time.value

            # Image Generation

            current_section_progress.value = 0.0
            print(
                ANSI_BLUE + "[4/4] " + ANSI_RESET + "Image Generation    " +
                "  0.00% " + ANSI_BLUE + "█" * 20 + ANSI_RESET
            )

            results = []
            for i in range(width.value * height.value):
                results.append(pool.apply_async(generate_image,
                    (i % width.value, i // width.value, width.value * height.value)))
            [result.wait() for result in results]

            time_now = time.time()
            section_times[1] = time_now - start_time.value

        except:
            raise_error("Pool Parent Process", traceback.format_exc())
    
    print(
        ANSI_GREEN + "Generation Complete " + ANSI_RESET +
        format_time(time.time() - start_time.value)
    )

    image = PIL.Image.new("RGB", (width.value, height.value), (255, 51, 133))
    image_pixels = image.load()
    for y in range(height.value):
        for x in range(width.value):
            image_pixels[x, y] = pixels[y][x]
    image.save("result.png")
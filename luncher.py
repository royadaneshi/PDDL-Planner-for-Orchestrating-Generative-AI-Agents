import subprocess
import os
import sys
import time


def check_and_install_python_packages():
    packages = {
        "pddl": "pddl",
        "pandas": "pandas",
        "tabulate": "tabulate",
        "transformers": "transformers",
        "torch": "torch",
        "requests": "requests",
        "time": "time"

    }

    for module_name, pip_name in packages.items():
        try:
            __import__(module_name)
            print(f"______________________________ {module_name} is already installed")
        except ImportError:
            print(f"______________________________ Installing {pip_name}...")
            subprocess.run([sys.executable, "-m", "pip", "install", pip_name], check=True)


def install_FD_planner():
    fd_dir = "./downward"
    if not os.path.exists(fd_dir):
        print("--- Downloading Fast Downward ---")
        try:
            subprocess.run([
                "git", "clone",
                "https://github.com/aibasel/downward.git",
                fd_dir
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone Fast Downward: {e}")
            return
    fd_executable = os.path.join(fd_dir, "builds/release/bin/downward")
    if os.path.exists(fd_executable):
        print("--- Fast Downward is already built. Skipping build step. ---")
    else:
        build_script = os.path.join(fd_dir, "build.py")
        if os.path.exists(build_script):
            print("--- Building Fast Downward (Release) - This may take a while ---")
            try:
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", "cmake", "g++", "make", "python3-dev"], check=True)

                subprocess.run(["./build.py", "release"], cwd=fd_dir, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during Fast Downward build: {e}")
        else:
            print("Error: build.py not found in the downward directory.")


def run():
    check_and_install_python_packages()
    install_FD_planner()

    print("--- Starting Ollama Server ---")
    subprocess.Popen(["ollama", "serve"], stdout=open("ollama.log", "w"), stderr=subprocess.STDOUT)

    # wait for the GPU to initialize
    time.sleep(10)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    # print("--- Running PDDL Planner ---")
    # subprocess.run(["/usr/bin/python3", "./run_pddl_planner.py"], env=env)

    # We define a fixed buggy plan at the beginning of our system,
    # so the system encounters possible failures, and we can observe how it recovers from them.
    plan = """(book-flight am415 t10-30 c195 denver chicago t07-55)
    (book-taxi uberx t13-30 c30 am415 t10-30)
    (book-hotel hyattregency t16-00 c220 uberx t13-30)"""

    with open("pddl_model/OrchestrationPlan.plan", "w") as f:
        f.write(plan)
    print(plan)

    print("--- Starting Travel Organizer Agent ---")
    subprocess.run(["/usr/bin/python3", "./main.py"], env=env)


if __name__ == "__main__":
    run()

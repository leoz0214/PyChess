"""Run this file to start the game up."""
import pathlib
import sys


if sys.version_info < (3, 10):
    print("Python version too low. Minimum supported: 3.10")
    sys.exit(1)


FOLDER = pathlib.Path(__file__).parent
sys.path.append(str(FOLDER / "src"))


from src import main


if __name__ == "__main__":
    main.main()

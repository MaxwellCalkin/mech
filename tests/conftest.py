import os
import sys

# Add the src directory to sys.path so test modules can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

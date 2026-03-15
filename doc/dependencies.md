# Dependencies

This project requires the following Python packages:

- **pygame**: For game window, rendering, and event handling.
- **pytest**: For running unit tests.
- **hypothesis**: For property-based testing.

## Installation Instructions

1.  **Ensure Python 3.10+ is installed**.
2.  **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # .env\Scripts\activate  # On Windows
    ```
3.  **Install packages using pip**:
    ```bash
    pip install pygame pytest hypothesis
    ```

**Note**: If you encounter issues with Python being externally managed (PEP 668), you may need to install `python3-pip` and `python3-venv` via your system's package manager (e.g., `sudo apt install python3-pip python3-venv`). Afterwards, you can create a virtual environment as described above.

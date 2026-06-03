"""
Command-line entry point for the SafeLicensing Streamlit application.

Invoked via the ``safelicensing`` console script installed by pip.
Any extra arguments after ``safelicensing`` are forwarded to Streamlit,
e.g.::

    safelicensing --server.port 8502
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """
    Launch the SafeLicensing Streamlit web application.

    Resolves the ``app.py`` module bundled inside the installed package,
    then delegates to ``streamlit run`` using the same Python interpreter
    that is running this entry point. Any CLI arguments after the command
    name are forwarded to Streamlit verbatim.

    :return: None. This function blocks until the Streamlit server exits,
             then propagates its exit code to the calling shell.
    """
    app_path = Path(__file__).parent / "app.py"

    if not app_path.is_file():
        print(
            f"Error: Streamlit app not found at expected path: {app_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)] + sys.argv[1:],
        check=False,
    )
    sys.exit(result.returncode)

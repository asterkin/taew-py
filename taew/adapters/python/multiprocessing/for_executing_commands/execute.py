"""Multiprocessing-based command executor for isolated CLI testing.

Executes commands in separate processes using multiprocessing to ensure
complete isolation between test runs and enable full coverage measurement.
"""

import importlib
import io
import multiprocessing
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from taew.domain.cli import CommandLine, Result


def _run_command_in_process(
    module_path: str,
    argv: list[str],
    queue: multiprocessing.Queue,  # type: ignore[type-arg]
) -> None:
    """Worker function to run command in separate process.

    Args:
        module_path: Module path to import (e.g., "bin.say")
        argv: Command line arguments
        queue: Multiprocessing queue for returning results
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    returncode = 0

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Import the module
            module = importlib.import_module(module_path)

            # Get and call main() function
            if not hasattr(module, "main"):
                raise OSError(f"Command module '{module_path}' has no main() function")

            main = module.main
            main(argv)

    except SystemExit as e:
        # Capture exit code from SystemExit
        returncode = int(e.code) if e.code is not None else 0
    except Exception as e:
        # Capture any other exceptions as stderr
        stderr_buffer.write(f"Error: {e}\n")
        returncode = 1

    # Send results back through queue
    queue.put((stdout_buffer.getvalue(), stderr_buffer.getvalue(), returncode))  # pyright: ignore[reportUnknownMemberType]


@dataclass(frozen=True, eq=False)
class Execute:
    """Multiprocessing-based command executor for isolated CLI testing.

    Executes CLI commands in separate processes using multiprocessing.Process.
    This provides complete isolation between test runs, preventing state leakage
    and side effects while still enabling full coverage measurement via
    coverage's multiprocessing support.

    Each command runs in its own process:
    1. Converts command path (e.g., "./bin/say") to module path (e.g., "bin.say")
    2. Spawns a new process
    3. In the child process: imports module, calls main(argv), captures output
    4. Returns Result with captured stdout, stderr, and exit code

    Example:
        >>> from taew.domain.cli import CommandLine
        >>> execute = Execute()
        >>> cmd = CommandLine(command="./bin/say", args=("--version",))
        >>> result = execute(cmd)
        >>> print(result.stdout)
        0.1.0
    """

    def __call__(self, command_line: CommandLine) -> Result:
        """Execute a command in a separate process.

        Imports the CLI entry point module in a child process and calls its
        main() function with captured stdout/stderr. This provides full
        integration testing with complete isolation between runs.

        Args:
            command_line: Command specification to execute

        Returns:
            Result containing captured stdout, stderr, and exit code

        Raises:
            ValueError: If command path is absolute
            OSError: If module cannot be imported or has no main() function

        Note:
            Environment variables from command_line.env are ignored since
            multiprocessing shares the parent process environment.
            Use os.environ directly in test setup if needed.
        """
        # Convert command path to module path
        # "./bin/say" -> "bin.say"
        # "bin/say" -> "bin.say"
        command_path = Path(command_line.command)
        if command_path.is_absolute():
            raise ValueError(
                f"Absolute command paths not supported: {command_line.command}"
            )

        # Remove ./ prefix and convert path separators to dots
        module_path = str(command_path).lstrip("./").replace("/", ".")

        # Build argv: [command, *args]
        argv = [command_line.command, *command_line.args]

        # Create queue for inter-process communication
        queue: multiprocessing.Queue = multiprocessing.Queue()  # type: ignore[type-arg]

        # Create and start process
        process = multiprocessing.Process(
            target=_run_command_in_process,  # pyright: ignore[reportUnknownArgumentType]
            args=(module_path, argv, queue),  # pyright: ignore[reportUnknownArgumentType]
        )
        process.start()
        process.join()

        # Get results from queue
        try:
            stdout, stderr, returncode = queue.get(timeout=1)  # pyright: ignore[reportUnknownVariableType]
        except Exception:
            # If queue is empty, process failed to send results
            return Result(
                stdout="",
                stderr=f"Process failed to execute {module_path}",
                returncode=1,
            )

        return Result(
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
        )

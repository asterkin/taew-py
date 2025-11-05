"""Multiprocessing-based command executor for isolated CLI testing.

Executes commands in separate processes using multiprocessing to ensure
complete isolation between test runs and enable full coverage measurement.
"""

import importlib.util
import io
import multiprocessing
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from taew.domain.cli import CommandLine, Result


def _run_command_in_process(
    command_path: str,
    argv: list[str],
    queue: "multiprocessing.Queue[tuple[str, str, int]]",
) -> None:
    """Worker function to run command in separate process.

    Args:
        command_path: Command file path (e.g., "./bin/bz" or "./bin/module.py")
        argv: Command line arguments
        queue: Multiprocessing queue for returning results
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    returncode = 0

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            file_path = Path(command_path)

            if not file_path.exists():
                raise OSError(f"Command file '{file_path}' does not exist")

            # Strategy 1: .py files → load as module from file
            if file_path.suffix == ".py":
                # Load module from file path using importlib.util
                module_name = file_path.stem
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    raise OSError(f"Cannot load module from '{file_path}'")

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "main"):
                    raise OSError(
                        f"Command module '{file_path}' has no main() function"
                    )

                main = module.main

            # Strategy 2: No extension → read and exec (shim files)
            elif file_path.suffix == "":
                with open(file_path, encoding="utf-8") as f:
                    code = f.read()

                # Execute in isolated namespace without __name__ == "__main__"
                namespace: dict[str, object] = {
                    "__name__": "__executed_module__",
                    "__file__": str(file_path),
                }
                exec(compile(code, str(file_path), "exec"), namespace)

                if "main" not in namespace:
                    raise OSError(f"Command file '{file_path}' has no main() function")

                main = namespace["main"]  # type: ignore[assignment]

            else:
                raise OSError(f"Unsupported file extension: {file_path.suffix}")

            # Call main() with argv directly
            main(argv)  # type: ignore[operator]

    except SystemExit as e:
        # Capture exit code from SystemExit
        returncode = int(e.code) if e.code is not None else 0
    except Exception as e:
        # Capture any other exceptions as stderr
        stderr_buffer.write(f"Error: {e}\n")
        returncode = 1

    # Send results back through queue
    queue.put((stdout_buffer.getvalue(), stderr_buffer.getvalue(), returncode))


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

        Executes CLI commands by either importing Python modules (.py files)
        or directly executing shim files (no extension) in a child process.
        Calls the command's main() function with captured stdout/stderr.

        Args:
            command_line: Command specification to execute

        Returns:
            Result containing captured stdout, stderr, and exit code

        Raises:
            ValueError: If command path is absolute
            OSError: If command file cannot be executed or has no main() function

        Note:
            Environment variables from command_line.env are ignored since
            multiprocessing shares the parent process environment.
            Use os.environ directly in test setup if needed.
        """
        # Validate command path
        command_path = Path(command_line.command)
        if command_path.is_absolute():
            raise ValueError(
                f"Absolute command paths not supported: {command_line.command}"
            )

        # Build argv: [command, *args]
        argv = [command_line.command, *command_line.args]

        # Create queue for inter-process communication
        queue: "multiprocessing.Queue[tuple[str, str, int]]" = multiprocessing.Queue()

        # Create and start process
        process = multiprocessing.Process(
            target=_run_command_in_process,  # pyright: ignore[reportUnknownArgumentType]
            args=(command_line.command, argv, queue),  # pyright: ignore[reportUnknownArgumentType]
        )
        process.start()
        process.join()

        # Get results from queue
        try:
            stdout, stderr, returncode = queue.get(timeout=5)
        except Exception:
            # If queue is empty, process failed to send results
            return Result(
                stdout="",
                stderr=f"Process failed to execute {command_line.command}",
                returncode=1,
            )

        return Result(
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
        )

"""Testing utilities for CLI applications.

Provides framework-agnostic utilities for testing CLI applications,
including output normalization for non-deterministic data.
"""

import re


def normalize_timing_data(text: str) -> str:
    """Normalize timing and non-deterministic data in CLI output.

    Replaces timestamps, datetime objects, UUIDs, and other hard-to-predict
    values with stable placeholders for reliable test assertions.

    Args:
        text: Raw CLI output text

    Returns:
        Normalized text with placeholders for non-deterministic values

    Example:
        >>> output = "Created at datetime.datetime(2025, 1, 15, 10, 30, 0)"
        >>> normalize_timing_data(output)
        'Created at <DATETIME>'

        >>> output = "ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        >>> normalize_timing_data(output)
        'ID: <UUID>'
    """
    # Replace timestamp parameters with datetime objects
    text = re.sub(
        r"timestamp=datetime\.datetime\([^)]+\)",
        "timestamp=<TIMESTAMP>",
        text,
    )

    # Replace general datetime objects
    text = re.sub(
        r"datetime\.datetime\([^)]+\)",
        "<DATETIME>",
        text,
    )

    # Replace UUIDs
    text = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "<UUID>",
        text,
    )

    return text

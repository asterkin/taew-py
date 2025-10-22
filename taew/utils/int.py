"""Integer utilities for width/size calculations.

These helpers are shared across adapters to compute minimal byte widths
for signed and unsigned integers using only Python stdlib features.
"""


def signed_int_bytes_needed(value: int) -> int:
    """Return minimal number of bytes to represent a signed int in two's complement.

    Includes the sign bit for positive values as required by int.to_bytes(signed=True).
    """
    if value == 0:
        return 1
    if value > 0:
        bits = value.bit_length() + 1  # include sign bit
    else:
        bits = (~value).bit_length() + 1  # two's complement width
    return max(1, (bits + 7) // 8)


def unsigned_int_bytes_needed(value: int) -> int:
    """Return minimal number of bytes to represent an unsigned int."""
    if value <= 0:
        return 1
    return (value.bit_length() + 7) // 8

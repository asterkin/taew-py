from typing import Any

from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


def _configure_sequence(*, _args: tuple[Any, ...]) -> ConfigureProtocol:
    from taew.adapters.python.tuple.sequence.for_streaming_objects.for_configuring_adapters import (
        Configure as ConfigureSequence,
    )

    return ConfigureSequence(_args=_args)


def _configure_record_and_sequence(*, _args: tuple[Any, ...]) -> ConfigureProtocol:
    from taew.adapters.python.tuple.record_and_sequence.for_streaming_objects.for_configuring_adapters import (
        Configure as ConfigureRecordAndSequence,
    )
    from taew.adapters.python.tuple.record.for_streaming_objects.for_configuring_adapters import (
        Configure as ConfigureRecord,
    )
    from taew.adapters.python.tuple.sequence.for_streaming_objects.for_configuring_adapters import (
        Configure as ConfigureSequence,
    )

    head_types = _args[:-2]
    tail_type = _args[-2]

    head_cfg = ConfigureRecord(_args=head_types)
    tail_cfg = ConfigureSequence(_args=(tail_type,))
    return ConfigureRecordAndSequence(
        _head=head_cfg, _tail=tail_cfg, _head_length=len(head_types)
    )


def _configure_record(*, _args: tuple[Any, ...]) -> ConfigureProtocol:
    from taew.adapters.python.tuple.record.for_streaming_objects.for_configuring_adapters import (
        Configure as ConfigureRecord,
    )

    return ConfigureRecord(_args=_args)


def Configure(_args: tuple[Any, ...]) -> ConfigureProtocol:
    """Factory function to create appropriate tuple configurator based on _args."""
    if not _args:
        raise ValueError("Tuple configuration requires at least one type")

    # Case 1: Record and sequence tuple - tuple[T1, T2, T3, ...]
    if _args[-1] is Ellipsis:
        len_args = len(_args)
        if len_args < 2:
            raise ValueError("Ellipsis tuple requires at least two entries")
        elif len_args == 2:
            return _configure_sequence(_args=(_args[0],))
        else:
            return _configure_record_and_sequence(_args=_args)
    return _configure_record(_args=_args)

from dataclasses import dataclass, field


@dataclass(eq=False, frozen=True)
class BuildBase:
    _variants: dict[type, str | dict[str, object]] = field(default_factory=lambda: {})

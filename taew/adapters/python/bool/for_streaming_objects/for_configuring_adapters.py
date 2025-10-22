from taew.adapters.python.choices.for_streaming_objects.for_configuring_adapters import (
    Configure as ChoicesConfigure,
)


class Configure(ChoicesConfigure):
    def __init__(self) -> None:
        # Initialize choices framing with False/True
        super().__init__(_choices=(False, True))

class FunctionInvocationError(Exception):
    def __init__(self, function_name: str, error_type: str, details: str):
        self.function_name = function_name
        self.error_type = error_type
        super().__init__(f"Function '{function_name}' {error_type}: {details}")

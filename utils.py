from typing import List, Dict, Any

class Ref:
    def __init__(self, *subscripts: tuple[str]) -> None:
        self.subscripts = list(subscripts)
        
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Ref):
            return False
        
        return self.subscripts == value.subscripts
        
    def __str__(self) -> str:
        return "/".join(self.subscripts)
    
class DIError:
    def __init__(self, message: str, supplementaryData: dict = None) -> None:
        self.message = message
        try:
            self.source = message[:message.index(":")]
        except:
            self.source = None
        self.supplementaryData = supplementaryData
        
    def __str__(self) -> str:
        return self.message
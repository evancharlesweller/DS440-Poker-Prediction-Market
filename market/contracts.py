from dataclasses import dataclass
from typing import Optional


@dataclass
class Contract:
    contract_id: str
    description: str
    contract_type: str
    target: Optional[str] = None
    target_player: Optional[str] = None
    price: float = 0.0

    # Lifecycle
    is_open: bool = True
    resolved: bool = False
    outcome: Optional[bool] = None

    def status_text(self) -> str:
        if self.resolved:
            return "RESOLVED"
        if self.is_open:
            return "OPEN"
        return "CLOSED"
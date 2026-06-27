from dataclasses import dataclass
from typing import Optional


@dataclass
class Contract:
    contract_id: str
    description: str
    contract_type: str
    target: Optional[str] = None
    price: float = 0.0

    # Lifecycle
    is_open: bool = True
    resolved: bool = False
    outcome: Optional[bool] = None

    # Closure rules
    closes_after_street: Optional[str] = None
    close_immediately_on_street_reveal: bool = False

    def status_text(self) -> str:
        if self.resolved:
            return "RESOLVED"
        if self.is_open:
            return "OPEN"
        return "CLOSED"
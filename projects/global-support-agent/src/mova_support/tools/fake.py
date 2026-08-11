from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class FakeSupportTools:
    """Development-only adapter. Never connects to production systems."""

    tickets: dict[str, dict[str, str]] = field(default_factory=dict)

    def create_human_ticket(
        self,
        *,
        session_id: UUID,
        model: str,
        reason: str,
    ) -> str:
        ticket_id = f"FAKE-{len(self.tickets) + 1:05d}"
        self.tickets[ticket_id] = {
            "session_id": str(session_id),
            "model": model,
            "reason": reason,
        }
        return ticket_id

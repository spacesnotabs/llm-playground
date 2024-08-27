from dataclasses import dataclass


@dataclass
class BasicMessage:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

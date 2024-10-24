from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BasicMessage:
    """
    Represents a basic message with a role and content.
    """
    role: str
    """
    The role of the message sender, e.g., "user" or "assistant".
    """
    content: str
    """
    The content of the message.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the BasicMessage object to a dictionary.

        Returns:
            A dictionary representation of the BasicMessage object.
        """
        return {"role": self.role, "content": self.content}

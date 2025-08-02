"""Telegram text escaping"""
from typing import List
import re

class TelegramFormatter:
    """Telegram special character escaping"""
    _SPECIAL_CHARS = '_[]()~>#+-=|{}.!'

    @classmethod
    def escape_text(cls, text: str) -> str:
        """Escape special characters with correct bold text support"""
        if not isinstance(text, str):
            return str(text)

        for char in cls._SPECIAL_CHARS:
            text = text.replace(char, '\\' + char)

        bold_pattern = r'\*([^*\n]+?)\*'
        bold_matches = list(re.finditer(bold_pattern, text))

        temp_markers = {}
        for i, match in enumerate(reversed(bold_matches)):
            marker = f"__BOLD_MARKER_{i}__"
            temp_markers[marker] = f"*{match.group(1)}*"
            text = text[:match.start()] + marker + text[match.end():]

        text = text.replace('*', '\\*')

        for marker, bold_text in temp_markers.items():
            text = text.replace(marker, bold_text)

        return text

    @classmethod
    def format_message(cls, text: str, max_length: int = 4096) -> List[str]:
        """Split long messages"""
        escaped_text = cls.escape_text(text)
        if len(escaped_text) <= max_length:
            return [escaped_text]

        parts = []
        while escaped_text:
            if len(escaped_text) <= max_length:
                parts.append(escaped_text)
                break

            split_point = max(
                escaped_text.rfind('\n', 0, max_length),
                escaped_text.rfind(' ', 0, max_length)
            )

            if split_point == -1:
                split_point = max_length

            parts.append(escaped_text[:split_point])
            escaped_text = escaped_text[split_point:].lstrip()

        return parts
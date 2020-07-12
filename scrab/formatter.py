from typing import List

from scrab.parser import NodeSequence


def to_text(content: List[NodeSequence]) -> str:
    return "\n".join(map(lambda nodes: nodes.to_formatted_text, content))

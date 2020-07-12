from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from functools import reduce, cached_property
from typing import Optional, List, Tuple, Set, Deque

from lxml.html import document_fromstring, HtmlElement


@dataclass
class Node:
    text: str
    tail: str
    visit_time: int
    tag: str

    @cached_property
    def token_cont(self) -> int:
        return len(self.tokens)

    @cached_property
    def tokens(self) -> List[str]:
        words = self.content
        return [] if len(words) == 0 else words.split(' ')

    @cached_property
    def content(self) -> str:
        stripped_text = self.text.strip()
        stripped_tail = self.tail.strip()

        text = stripped_text if len(stripped_text) == 0 else self.text
        tail = stripped_tail if len(stripped_tail) == 0 else self.tail

        return text + tail

    @cached_property
    def formatted_content(self) -> str:
        h_tags = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
        if self.tag in h_tags:
            return "\n" + self.content + "\n"
        elif self.tag == "p":
            return "\n" + self.content
        else:
            return self.content


@dataclass
class NodeSequence:
    nodes: List[Node]

    def __init__(self, nodes: List[Node]):
        if len(nodes) == 0:
            raise ValueError("Provided nodes are empty.")
        self.nodes = nodes

    @cached_property
    def word_count(self) -> int:
        return reduce(lambda a, b: a + b, [node.token_cont for node in self.nodes], 0)

    @cached_property
    def entry_time(self) -> int:
        return min(node.visit_time for node in self.nodes)

    @cached_property
    def exit_time(self) -> int:
        return max(node.visit_time for node in self.nodes)

    @cached_property
    def to_text(self, separator: str = "") -> str:
        return separator.join(node.content for node in self.nodes)

    @cached_property
    def to_formatted_text(self, separator: str = "") -> str:
        return separator.join(node.formatted_content for node in self.nodes)

    @cached_property
    def tokens(self) -> List[str]:
        return [node_token for node in self.nodes for node_token in node.tokens]


class NodeState(IntEnum):
    discovered = 1
    processed = 2


def parse(html_page: str) -> List[NodeSequence]:
    """
    - Traverse the html tree with DFS and store visit time of each node
    - Connect consecutive html nodes
    - Fuzzy clean all non-content nodes
    """

    dfs_stack: Deque[HtmlElement] = deque()
    time = 0

    def append_children(html_node: HtmlElement) -> None:
        # append_children modes on the left side, to preserve tag order on pop()
        reverse = list(html_node)
        reverse.reverse()
        dfs_stack.extend(reverse)

    # TODO extract title
    root: HtmlElement = document_fromstring(html_page).body
    append_children(root)

    text_nodes: Deque[Node] = deque()

    while dfs_stack:
        current = dfs_stack.pop()

        if type(current) is not HtmlElement:
            continue

        time += 1

        if hasattr(current, 'state') and current.state == NodeState.discovered:
            # current was already visited, implies that all children are already visited
            current.state = NodeState.processed

        elif hasattr(current, 'state') and current.state == NodeState.processed:
            raise RuntimeError('This state is illegal, because an processed element was pushed to the stack.')

        else:
            current.state = NodeState.discovered
            node = Node(current.text or '', current.tail or '', time, current.tag)
            if node.token_cont > 0:
                text_nodes.append(node)

            if len(current) > 0:
                # current node has children
                dfs_stack.append(current)
                append_children(current)

            else:
                # no children
                current.exit_time = time
                current.state = NodeState.processed

    def join_consecutive(nodes: List[NodeSequence]) -> List[NodeSequence]:
        previous: Optional[NodeSequence] = None
        result: List[NodeSequence] = []

        for current_node in nodes:
            if previous is not None:
                if abs(previous.exit_time - current_node.entry_time) == 1:
                    previous = NodeSequence(previous.nodes + current_node.nodes)
                else:
                    result.append(previous)
                    previous = current_node
            else:
                previous = current_node

        if previous is not None:
            result.append(previous)

        if len(result) < len(nodes):
            return join_consecutive(result)
        else:
            return result

    node_seq = [NodeSequence([node]) for node in text_nodes]

    joined_nodes = join_consecutive(node_seq)
    cleaned_nodes = clean(joined_nodes)

    return cleaned_nodes


def clean(seq: List[NodeSequence]) -> List[NodeSequence]:
    """
    Basic idea:
    - Traverses each node windowed by the surrounding nodes
    - Decides if the node is probably a content node
    """

    def fuzzy_clean(context: List[NodeSequence], current: int) -> Optional[NodeSequence]:
        """
        Heuristic approach based on degrees of belief and disbelief.

        Assumptions:
        - Content has high text ratio
        - Content snippets have similar formatting and as a result follow an equal pattern, e.g. <div> -> <p> -> text
        - Content is located on similar depth in DOM

        Heuristic rules:
        1. number_nodes: Does given NodeSequence has more then one consecutive nodes?
        2. allowlist/blocklist: Does given NodeSequence has nodes with allowed/blocked tags?
        3. tag_variation: Does given consecutive nodes have the same tag, e.g. <p>?
        4. word_count: Number of words contained in all nodes
        5. neighborhood: Given NodeSequences within a window, how different is the depth difference in the DOM?
        6. word ratio: Typical sentences usually have word containing alphanumeric chars
        """

        # Degrees of belief/disbelief
        zero = .0
        low = .25
        high = .5
        very_high = .75
        certain = 1.

        current_node = context[current]

        if len(current_node.nodes) > 1:
            number_nodes_belief = high
            number_nodes_disbelief = zero
        else:
            number_nodes_belief = zero
            number_nodes_disbelief = low

        allowlist = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'}
        tag_blocklist = {'script', 'time', 'button', 'style'}

        tags = {node.tag for node in current_node.nodes}
        alowlist_belief = certain if len(tags & allowlist) > 0 else zero
        blocklist_disbelief = certain if len(tags & tag_blocklist) > 0 else zero

        def tag_variation(tags: Set[str], nodes: int) -> Tuple[float, float]:
            belief = zero
            disbelief = zero

            if len(tags) == 1 and nodes > 1:
                belief = low
            elif len(tags) == nodes:
                disbelief = low

            return belief, disbelief

        tag_variation_belief, tag_variation_disbelief = tag_variation(tags, len(current_node.nodes))

        def word_count(current_node: NodeSequence) -> Tuple[float, float]:
            belief = zero
            disbelief = zero

            word_count = current_node.word_count / len(current_node.nodes)

            if word_count > 20:
                belief = certain
            elif word_count > 10:
                belief = very_high
            elif word_count > 7:
                belief = high
            elif word_count > 5:
                belief = low
            elif word_count <= 1:
                disbelief = high
            elif word_count < 3:
                disbelief = low

            return belief, disbelief

        number_words_belief, number_words_disbelief = word_count(current_node)

        def neighborhood(context_window: List[NodeSequence], current_index: int) -> Tuple[float, float]:
            belief = zero
            disbelief = zero

            exit_times = [node.exit_time for node in context_window]
            entry_times = [node.entry_time for node in context_window]
            periods = zip(entry_times[1:], exit_times[:-1])
            diff = [period[0] - period[1] for period in periods]

            if len(set(diff)) == 1:
                time_diff = diff[0]
                if time_diff < 2:
                    belief = high
                elif time_diff < 4:
                    belief = low
                elif time_diff > 5:
                    disbelief = very_high

            else:
                diff_before = diff[:current_index]
                diff_after = diff[current_index:]

                def decay_sum(numbers: List[int]) -> float:
                    denominator = 1.
                    result_sum = 0.
                    for n in numbers:
                        result_sum += float(n) / denominator
                        denominator *= 2.
                    return result_sum

                diff_before.reverse()
                sum_before = decay_sum(diff_before)
                sum_after = decay_sum(diff_after)

                if sum_before < 3. and sum_after < 3.:
                    belief = low
                elif sum_before < 6. and sum_after < 6.:
                    disbelief = low
                else:
                    disbelief = certain

            return belief, disbelief

        neighborhood_belief, neighborhood_disbelief = neighborhood(context, current)

        def word_ratio(current_node: NodeSequence) -> Tuple[float, float]:
            belief = zero
            disbelief = zero

            tokens = current_node.tokens

            if len(tokens) > 10:
                ratios = [int(token.isalpha()) for token in tokens]
                word_ratio = sum(ratios) / len(tokens)
                if word_ratio > 0.85:
                    belief = very_high
                elif word_ratio > 0.8:
                    belief = high
                elif word_ratio < 0.1:
                    disbelief = very_high
                elif word_ratio < 0.2:
                    disbelief = high
                elif word_ratio < 0.5:
                    disbelief = low

            return belief, disbelief

        word_ratio_belief, word_ratio_disbelief = word_ratio(current_node)

        beliefs = [number_nodes_belief,
                   alowlist_belief,
                   tag_variation_belief,
                   number_words_belief,
                   neighborhood_belief,
                   word_ratio_belief]

        disbeliefs = [number_nodes_disbelief,
                      blocklist_disbelief,
                      tag_variation_disbelief,
                      number_words_disbelief,
                      neighborhood_disbelief,
                      word_ratio_disbelief]

        certainty = sum(beliefs) - sum(disbeliefs)

        return current_node if certainty >= very_high else None

    def next_window(i: int, window_size: int) -> Tuple[int, int]:
        left = i - window_size
        left = left if left > 0 else 0
        right = i + window_size + 1
        right = right if right < len(seq) else len(seq)
        return left, right

    context_size = 2
    cleaned_result = []

    for current in range(0, len(seq)):
        left, right = next_window(current, context_size)
        context = seq[left:right]
        cleaned = fuzzy_clean(context, current - left)

        if cleaned is not None:
            cleaned_result.append(cleaned)

    return cleaned_result

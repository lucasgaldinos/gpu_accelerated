"""Utilities for converting Angular chat HTML into readable Markdown.

This module ingests the HTML export of a Google-style Angular chat UI and
renders a clean, structured Markdown transcript. It keeps conversational order,
preserves lists, headings, code blocks, and attempts to recover KaTeX formulas
back into LaTeX syntax so they survive Markdown previews.

The script is intentionally lightweight so it can be shared with learners
without requiring a complex environment. It relies only on BeautifulSoup for
parsing and markdownify for HTML-to-Markdown conversion.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence, cast

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from markdownify import MarkdownConverter


INLINE_MATH_SELECTOR = "span.math-inline"
BLOCK_MATH_SELECTOR = "div.math-block"


@dataclass
class Attachment:
    """Metadata about a file attachment referenced in the chat."""

    label: str
    icon_url: str | None
    file_type: str | None


@dataclass
class Message:
    """Represents a single turn in the conversation."""

    role: str
    index: int
    html: str
    attachments: Sequence[Attachment]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns
    -------
    argparse.Namespace
            Configuration containing the input HTML path, optional output path, and
            heading level for speaker labels.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Convert an Angular chat HTML export into structured Markdown with "
            "speaker headings, preserved lists, code blocks, and LaTeX math."
        )
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to the exported HTML conversation (e.g., ahhh.html).",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        dest="output_path",
        help="Optional path for the generated Markdown. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "--role-heading-level",
        type=int,
        default=2,
        help="Markdown heading level (## -> 2) used for speaker labels.",
    )
    return parser.parse_args()


def load_document(path: Path) -> BeautifulSoup:
    """Read and parse an HTML document.

    Parameters
    ----------
    path:
            Location of the HTML file.

    Returns
    -------
    BeautifulSoup
            Parsed soup tree using the standard HTML parser.
    """

    html_text = path.read_text(encoding="utf-8")
    return BeautifulSoup(html_text, "html.parser")


def extract_messages(soup: BeautifulSoup) -> list[Message]:
    """Extract user and assistant messages from the Angular conversation HTML."""

    messages: list[Message] = []
    user_counter = 0
    assistant_counter = 0
    for container in soup.select("div.conversation-container"):
        if container.select_one("user-query") is not None:
            user_counter += 1
            messages.append(parse_user_message(container, user_counter))

        model_response = container.select_one("model-response")
        if model_response is not None:
            assistant_counter += 1
            messages.append(parse_assistant_message(model_response, assistant_counter))

    return messages


def parse_user_message(container: Tag, index: int) -> Message:
    """Convert a user turn into a Message object."""

    attachments = list(collect_attachments(container))
    query_text = container.select_one("div.query-text")
    html = query_text.decode_contents() if query_text else ""
    return Message(role="User", index=index, html=html, attachments=attachments)


def parse_assistant_message(model_response: Tag, index: int) -> Message:
    """Convert a model response into a Message object."""

    content_root = model_response.select_one("message-content")
    content = content_root.select_one("div") if content_root else None
    if content is None:
        return Message(role="Assistant", index=index, html="", attachments=[])

    # Clone only the meaningful portion to avoid leaking control widgets.
    fragment = BeautifulSoup(content.decode_contents(), "html.parser")
    strip_ui_chrome(fragment)
    transform_math(fragment)

    html = fragment.decode()
    return Message(role="Assistant", index=index, html=html, attachments=[])


def collect_attachments(container: Tag) -> Iterable[Attachment]:
    """Yield attachments referenced in a user prompt."""

    for preview in container.select("div.new-file-preview-container"):
        label_tag = preview.select_one("div.new-file-name")
        file_type_tag = preview.select_one("div.new-file-type")
        icon_tag = preview.select_one("img.new-file-icon")
        yield Attachment(
            label=label_tag.get_text(strip=True) if label_tag else "",
            icon_url=_optional_attr(icon_tag, "src"),
            file_type=file_type_tag.get_text(strip=True) if file_type_tag else None,
        )


def strip_ui_chrome(fragment: BeautifulSoup) -> None:
    """Remove toolbar widgets, footers, and other UI-only elements."""

    for selector in [
        "button",
        "sources-list",
        "feedback-container",
        "footer",
        "sensitive-memories-banner",
        "tts-control",
        "response-container-footer",
    ]:
        for tag in fragment.select(selector):
            tag.decompose()


def transform_math(fragment: BeautifulSoup) -> None:
    """Replace KaTeX-rendered math with LaTeX strings."""

    for span in fragment.select(INLINE_MATH_SELECTOR):
        latex = katex_to_latex(span)
        span.replace_with(fragment.new_string(f"${latex}$"))

    for block in fragment.select(BLOCK_MATH_SELECTOR):
        latex = katex_to_latex(block)
        block.replace_with(fragment.new_string(f"\n$$\n{latex}\n$$\n"))


def katex_to_latex(node: Tag) -> str:
    """Best-effort translation of KaTeX HTML into LaTeX source."""

    html_span = node.select_one(".katex-html")
    if html_span is None:
        return node.get_text(strip=True)
    latex = normalise_katex(html_span)
    return compact_whitespace(latex)


def normalise_katex(node: Tag | NavigableString) -> str:
    """Recursively convert KaTeX DOM nodes to LaTeX tokens."""

    if isinstance(node, NavigableString):
        return str(node)

    classes = set(_as_list(node.get("class")))
    if not classes:
        return "".join(normalise_katex(child) for child in _iter_math_children(node))

    if "mspace" in classes:
        return "\\ "

    if "mfrac" in classes:
        return parse_fraction(node)

    if "msupsub" in classes:
        return parse_supsub(node)

    if classes & {"base", "katex-html", "vlist", "vlist-t", "vlist-r"}:
        return "".join(normalise_katex(child) for child in _iter_math_children(node))

    if classes & {"mord", "mop", "mrel", "mopen", "mclose", "mbin", "text"}:
        return "".join(normalise_katex(child) for child in _iter_math_children(node))

    if "sizing" in classes:
        return "".join(normalise_katex(child) for child in _iter_math_children(node))

    # Default fallback for any remaining spans.
    return node.get_text(strip=True)


STYLE_TOP_PATTERN = re.compile(r"top:\s*([-0-9.]+)em")


def parse_supsub(node: Tag) -> str:
    """Extract superscripts and subscripts from an msupsub node."""

    sup_components: list[str] = []
    sub_components: list[str] = []
    for sizing in node.select("span.sizing"):
        text = compact_whitespace(
            "".join(normalise_katex(child) for child in _iter_math_children(sizing))
        )
        if not text:
            continue
        style = _attribute_to_str(sizing.parent.get("style") if sizing.parent else None)
        match = STYLE_TOP_PATTERN.search(style)
        if match:
            position = float(match.group(1))
            if position < 0:
                sup_components.append(text)
            else:
                sub_components.append(text)
        else:
            sup_components.append(text)

    sup = "".join(sup_components)
    sub = "".join(sub_components)
    latex = ""
    if sup:
        latex += f"^{{{sup}}}"
    if sub:
        latex += f"_{{{sub}}}"
    return latex


def parse_fraction(node: Tag) -> str:
    """Convert a KaTeX fraction into LaTeX "\\frac" syntax."""

    groups: dict[float, list[str]] = {}
    for sizing in node.select("span.sizing"):
        text = compact_whitespace(
            "".join(normalise_katex(child) for child in _iter_math_children(sizing))
        )
        if not text:
            continue
        style = _attribute_to_str(sizing.parent.get("style") if sizing.parent else None)
        match = STYLE_TOP_PATTERN.search(style)
        key = float(match.group(1)) if match else 0.0
        groups.setdefault(key, []).append(text)

    if not groups:
        return node.get_text(strip=True)

    ordered = sorted(groups.items(), key=lambda item: item[0])
    numerator = "".join(ordered[0][1])
    denominator = "".join(ordered[-1][1])
    return f"\\frac{{{numerator}}}{{{denominator}}}"


def compact_whitespace(text: str) -> str:
    """Collapse consecutive whitespace while preserving single spaces."""

    return re.sub(r"\s+", " ", text).strip()


def _iter_math_children(node: Tag) -> Iterable[Tag | NavigableString]:
    """Yield child nodes that are relevant for math parsing."""

    for child in node.children:
        if isinstance(child, (Tag, NavigableString)):
            yield child


def _as_list(value: object | None) -> list[str]:
    """Normalise BeautifulSoup attribute values into a list of strings."""

    if value is None:
        return []
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [str(item) for item in items]
    return [str(value)]


def _attribute_to_str(value: object | None) -> str:
    """Convert a BeautifulSoup attribute value into a plain string."""

    if value is None:
        return ""
    if isinstance(value, list):
        parts = cast(list[Any], value)
        return " ".join(str(item) for item in parts)
    return str(value)


def _optional_attr(tag: Tag | None, attribute: str) -> str | None:
    """Fetch an optional attribute from a tag, returning ``None`` when empty."""

    if tag is None:
        return None
    value = _attribute_to_str(tag.get(attribute))
    return value or None


def convert_html_to_markdown(html: str) -> str:
    """Turn sanitized HTML into Markdown with predictable spacing."""

    converter = MarkdownConverter(bullets="-", strip=[])
    markdown = converter.convert(html)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def render_message(message: Message, heading_level: int) -> str:
    """Render a single message into Markdown."""

    heading_prefix = "#" * max(1, heading_level)
    title = f"{heading_prefix} {message.role} {message.index}"
    parts = [title, ""]

    if message.attachments:
        parts.append("**Attachments:**")
        for attachment in message.attachments:
            icon = f"![icon]({attachment.icon_url}) " if attachment.icon_url else ""
            file_type = f" ({attachment.file_type})" if attachment.file_type else ""
            parts.append(f"- {icon}{attachment.label}{file_type}")
        parts.append("")

    if message.html:
        markdown_body = convert_html_to_markdown(message.html)
        markdown_body = re.sub(r"\n{3,}", "\n\n", markdown_body)
        if message.role.lower() == "user":
            paragraphs: list[str] = []
            for paragraph in markdown_body.split("\n\n"):
                lines: list[str] = [
                    line.strip() for line in paragraph.splitlines() if line.strip()
                ]
                if lines:
                    paragraphs.append(" ".join(lines))
            markdown_body = "\n\n".join(paragraphs)
        parts.append(markdown_body)

    return "\n".join(part for part in parts if part)


def render_conversation(messages: Sequence[Message], heading_level: int) -> str:
    """Aggregate all messages into a Markdown transcript."""

    rendered = [render_message(message, heading_level) for message in messages]
    return "\n\n".join(filter(None, rendered)) + "\n"


def generate_markdown(input_path: Path, heading_level: int) -> str:
    """High-level orchestration: parse HTML and produce Markdown text."""

    soup = load_document(input_path)
    messages = extract_messages(soup)
    return render_conversation(messages, heading_level)


def main() -> None:
    """Entry point for CLI execution."""

    args = parse_arguments()
    markdown = generate_markdown(args.input_path, args.role_heading_level)
    if args.output_path:
        args.output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()

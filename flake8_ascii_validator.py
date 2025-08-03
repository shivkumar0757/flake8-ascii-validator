"""
ASCII Validator Plugin for Flake8

This plugin checks for non-ASCII characters in Python source code
and reports them as style violations.
"""

import tokenize
from typing import Generator, Tuple

# TODO: Future enhancement - AST-based checking for more granular validation
# import ast


class AsciiChecker:
    """Flake8 plugin to check for non-ASCII characters in source code."""

    name = "flake8-ascii-validator"
    version = "1.0.2"

    # Error codes
    ASC001 = "ASC001 Non-ASCII character found in source code"
    ASC002 = "ASC002 Non-ASCII character found in string literal"
    ASC003 = "ASC003 Non-ASCII character found in comment"

    def __init__(
        self, tree, file_tokens: list = None, filename: str = "<unknown>"
    ):
        """Initialize the checker.

        Args:
            tree: The AST tree (not used in current implementation)
            file_tokens: List of tokens from the source file
            filename: Name of the file being checked
        """
        # Note: tree parameter kept for Flake8 compatibility but not used
        # TODO: Future - implement AST-based checking for precision
        self.file_tokens = file_tokens or []
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        """Run the ASCII validation checks.

        Yields:
            Tuple of (line_number, column_offset, message, checker_class)
        """
        # Simple token-based checking - sufficient for ASCII validation
        yield from self._check_tokens()

    def _check_tokens(
        self,
    ) -> Generator[Tuple[int, int, str, type], None, None]:
        """Check tokens for non-ASCII characters."""
        for token in self.file_tokens:
            if token.type == tokenize.COMMENT:
                yield from self._check_comment(token)
            elif token.type == tokenize.STRING:
                yield from self._check_string_token(token)
            else:
                yield from self._check_general_token(token)

    def _check_comment(
        self, token
    ) -> Generator[Tuple[int, int, str, type], None, None]:
        """Check comment tokens for non-ASCII characters."""
        comment_text = token.string
        for i, char in enumerate(comment_text):
            if ord(char) > 127:
                col_offset = token.start[1] + i
                yield (
                    token.start[0],
                    col_offset,
                    f"{self.ASC003} Non-ASCII character '{char}' "
                    f"(U+{ord(char):04X}) found in comment",
                    type(self),
                )
                break  # Report only first occurrence per comment

    def _check_string_token(
        self, token
    ) -> Generator[Tuple[int, int, str, type], None, None]:
        """Check string tokens for non-ASCII characters."""
        string_text = token.string

        # Skip checking string literals meant to contain Unicode
        # (like raw strings or those with encoding prefixes)
        if string_text.lower().startswith(
            ('r"', "r'", 'u"', "u'", 'b"', "b'")
        ):
            return

        for i, char in enumerate(string_text):
            if ord(char) > 127:
                col_offset = token.start[1] + i
                yield (
                    token.start[0],
                    col_offset,
                    f"{self.ASC002} Non-ASCII character '{char}' "
                    f"(U+{ord(char):04X}) found in string literal",
                    type(self),
                )
                break  # Report only first occurrence per string

    def _check_general_token(
        self, token
    ) -> Generator[Tuple[int, int, str, type], None, None]:
        """Check general tokens for non-ASCII characters."""
        # Skip certain token types that commonly contain Unicode
        skip_types = {tokenize.STRING, tokenize.COMMENT, tokenize.ENCODING}
        if token.type in skip_types:
            return

        token_text = token.string
        for i, char in enumerate(token_text):
            if ord(char) > 127:
                col_offset = token.start[1] + i
                yield (
                    token.start[0],
                    col_offset,
                    f"{self.ASC001} Non-ASCII character '{char}' "
                    f"(U+{ord(char):04X}) found in source code",
                    type(self),
                )
                break  # Report only first occurrence per token


# TODO: Future enhancement - AST-based checking for granular validation
# def _check_ast_nodes(
#     self,
# ) -> Generator[Tuple[int, int, str, type], None, None]:
#     """Check AST nodes for non-ASCII characters in string literals."""
#     for node in ast.walk(self.tree):
#         if isinstance(node, ast.Str):  # Python < 3.8 compatibility
#             yield from self._check_string_node(node)
#         elif isinstance(node, ast.Constant) and isinstance(node.value, str):
#             yield from self._check_string_node(node)
#
# def _check_string_node(
#     self, node
# ) -> Generator[Tuple[int, int, str, type], None, None]:
#     """Check string AST nodes for non-ASCII characters."""
#     if hasattr(node, 'value'):
#         string_value = node.value
#     elif hasattr(node, 's'):  # Python < 3.8
#         string_value = node.s
#     else:
#         return
#
#     if not isinstance(string_value, str):
#         return
#
#     for i, char in enumerate(string_value):
#         if ord(char) > 127:
#             yield (
#                 node.lineno,
#                 node.col_offset + i,
#                 f"{self.ASC002} Non-ASCII character '{char}' "
#                 f"(U+{ord(char):04X}) found in string literal",
#                 type(self)
#             )
#             break  # Report only first occurrence per string


# Entry point for the plugin
def ascii_checker_factory(tree, filename: str, file_tokens: list = None):
    """Factory function to create AsciiChecker instances."""
    return AsciiChecker(tree, file_tokens, filename)

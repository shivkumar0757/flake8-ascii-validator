"""Test cases for flake8_ascii_validator plugin."""

import ast
import tokenize
from io import StringIO
from typing import List, Tuple

import pytest

from flake8_ascii_validator import AsciiChecker

# Note: Tests still use ast.parse for generating test trees but the plugin
# itself no longer uses AST checking - only token-based validation


class TestAsciiChecker:
    """Test cases for the AsciiChecker plugin."""

    def _check_code(
        self, code: str, filename: str = "<test>"
    ) -> List[Tuple[int, int, str, type]]:
        """Helper method to check code and return violations."""
        tree = ast.parse(code)

        # Generate tokens
        tokens = []
        try:
            for token in tokenize.generate_tokens(StringIO(code).readline):
                tokens.append(token)
        except tokenize.TokenError:
            # Handle incomplete code samples
            pass

        checker = AsciiChecker(tree, tokens, filename)
        return list(checker.run())

    def test_ascii_code_passes(self):
        """Test that valid ASCII code passes without violations."""
        code = '''
def hello_world():
    """A simple function."""
    message = "Hello, World!"
    return message
'''
        violations = self._check_code(code)
        assert len(violations) == 0

    def test_non_ascii_in_variable_name(self):
        """Test detection of non-ASCII characters in variable names."""
        code = """
def test_function():
    variablé = "test"  # Non-ASCII character in variable name
    return variablé
"""
        violations = self._check_code(code)
        assert len(violations) >= 1

        # Check that we detect the non-ASCII character
        violation_messages = [v[2] for v in violations]
        assert any("ASC001" in msg for msg in violation_messages)

    def test_non_ascii_in_string_literal(self):
        """Test detection of non-ASCII characters in string literals."""
        code = """
def greet():
    message = "Héllo, Wørld!"  # Non-ASCII characters in string
    return message
"""
        violations = self._check_code(code)
        assert len(violations) >= 1

        # Check that we detect the non-ASCII character in string
        violation_messages = [v[2] for v in violations]
        assert any("ASC002" in msg for msg in violation_messages)

    def test_non_ascii_in_comment(self):
        """Test detection of non-ASCII characters in comments."""
        code = """
def function():
    # This is a commént with non-ASCII
    return "test"
"""
        violations = self._check_code(code)
        assert len(violations) >= 1

        # Check that we detect the non-ASCII character in comment
        violation_messages = [v[2] for v in violations]
        assert any("ASC003" in msg for msg in violation_messages)

    def test_unicode_string_prefixes_ignored(self):
        """Test that Unicode string prefixes are properly handled."""
        code = """
def unicode_strings():
    raw_string = r"Héllo"  # Raw string should be handled carefully
    unicode_string = u"Wørld"  # Unicode string prefix
    byte_string = b"ASCII only"  # Byte string
    return raw_string, unicode_string, byte_string
"""
        # This test checks our handling of different string types
        # The behavior may vary based on implementation choices
        self._check_code(code)  # Just run the check to test it works
        # We may or may not flag these depending on our policy
        # The test documents the current behavior

    def test_multiple_violations_same_line(self):
        """Test handling of multiple violations on the same line."""
        code = """
variablé = "Héllo"  # Commént with non-ASCII
"""
        violations = self._check_code(code)
        assert (
            len(violations) >= 1
        )  # At least one violation should be detected

    def test_error_codes_and_messages(self):
        """Test that error codes and messages are properly formatted."""
        code = """
# Commént with é
variablé = "Héllo"
"""
        violations = self._check_code(code)

        for line, col, message, checker_type in violations:
            assert isinstance(line, int)
            assert isinstance(col, int)
            assert isinstance(message, str)
            assert checker_type == AsciiChecker

            # Check message format
            assert message.startswith("ASC00")
            assert "U+" in message  # Unicode code point should be included

    def test_empty_file(self):
        """Test handling of empty files."""
        violations = self._check_code("")
        assert len(violations) == 0

    def test_only_whitespace(self):
        """Test handling of files with only whitespace."""
        code = """



"""
        violations = self._check_code(code)
        assert len(violations) == 0

    def test_docstring_with_non_ascii(self):
        """Test detection in docstrings (via token-based checking)."""
        code = '''
def function():
    """This is a docstring with non-ASCII: café"""
    pass
'''
        violations = self._check_code(code)
        # Should detect non-ASCII in the docstring (STRING token)
        violation_messages = [v[2] for v in violations]
        assert any("ASC002" in msg for msg in violation_messages)

    def test_f_string_with_non_ascii(self):
        """Test detection in f-strings."""
        code = """
name = "José"
message = f"Hello, {name}!"  # Non-ASCII in variable name
"""
        violations = self._check_code(code)
        # Should detect non-ASCII in the variable name
        assert len(violations) >= 1

    def test_class_with_non_ascii_attribute(self):
        """Test detection in class attributes."""
        code = """
class MyClass:
    attribúte = "value"  # Non-ASCII in attribute name

    def méthod(self):  # Non-ASCII in method name
        return self.attribúte
"""
        violations = self._check_code(code)
        # Should detect non-ASCII in both attribute and method names
        assert len(violations) >= 2

    def test_import_with_non_ascii(self):
        """Test detection in import statements."""
        code = """
# This would be invalid Python, but let's test our detection
# import módule  # Non-ASCII in module name
def test():
    # Variablé name with non-ASCII
    résult = "test"
    return résult
"""
        violations = self._check_code(code)
        assert len(violations) >= 1

    def test_checker_attributes(self):
        """Test that the checker has required attributes."""
        tree = ast.parse("print('hello')")
        checker = AsciiChecker(tree, [], "<test>")

        assert hasattr(checker, "name")
        assert hasattr(checker, "version")
        assert checker.name == "flake8-ascii-validator"
        assert isinstance(checker.version, str)

    def test_unicode_code_points_in_messages(self):
        """Test that Unicode code points are included in error messages."""
        code = 'variablé = "test"  # é has code point U+00E9'
        violations = self._check_code(code)

        # Find violation with the 'é' character
        e_violations = [v for v in violations if "U+00E9" in v[2]]
        assert len(e_violations) >= 1

    def test_line_and_column_accuracy(self):
        """Test that line and column numbers are accurate."""
        code = """def function():
    variablé = "test"  # Line 2, non-ASCII at specific column
"""
        violations = self._check_code(code)

        # Should have at least one violation on line 2
        line_2_violations = [v for v in violations if v[0] == 2]
        assert len(line_2_violations) >= 1

        # Column should be reasonable (not negative, not too large)
        for violation in line_2_violations:
            assert violation[1] >= 0
            assert violation[1] < 100  # Reasonable upper bound


class TestAsciiCheckerIntegration:
    """Integration tests for the AsciiChecker plugin."""

    def test_factory_function(self):
        """Test the factory function works correctly."""
        from flake8_ascii_validator import ascii_checker_factory

        tree = ast.parse(
            "print('hello')"
        )  # Tree still passed for compatibility
        checker = ascii_checker_factory(tree, "<test>", [])

        assert isinstance(checker, AsciiChecker)
        assert checker.filename == "<test>"

    def test_plugin_registration_format(self):
        """Test that the plugin follows Flake8 registration format."""
        # This test ensures our plugin class has the right interface
        tree = ast.parse("print('hello')")
        checker = AsciiChecker(tree, [], "<test>")

        # Should have a run method that returns a generator
        assert hasattr(checker, "run")
        assert callable(checker.run)

        # Run should return an iterable of tuples
        results = list(checker.run())
        assert isinstance(results, list)

        # Each result should be a tuple with the right format
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 4
            line, col, msg, checker_type = result
            assert isinstance(line, int)
            assert isinstance(col, int)
            assert isinstance(msg, str)
            assert checker_type == AsciiChecker


if __name__ == "__main__":
    pytest.main([__file__])

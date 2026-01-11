"""
Tests for directive parsing, specifically ISSUE-004: skip code blocks.

Directives inside fenced code blocks (``` or ~~~) should NOT be parsed
as real configuration. This prevents example directives in documentation
from affecting document processing.
"""

import pytest
from livemathtex.parser.lexer import Lexer


class TestDirectiveCodeBlockSkipping:
    """Tests for ISSUE-004: Directive parser should skip fenced code blocks."""

    def test_directive_in_backtick_code_block_ignored(self):
        """Directives inside ``` code blocks should NOT be parsed."""
        content = '''<!-- livemathtex: digits=4 -->

Example:
```markdown
<!-- livemathtex: output=inplace -->
```
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {'digits': 4}
        assert 'output' not in directives

    def test_directive_in_tilde_code_block_ignored(self):
        """Directives inside ~~~ code blocks should NOT be parsed."""
        content = '''<!-- livemathtex: format=engineering -->

~~~
<!-- livemathtex: digits=2 -->
~~~
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {'format': 'engineering'}
        assert 'digits' not in directives

    def test_multiple_code_blocks_all_ignored(self):
        """Multiple code blocks should all be stripped."""
        content = '''<!-- livemathtex: digits=6 -->

First code block:
```
<!-- livemathtex: digits=2 -->
```

Second code block:
~~~python
<!-- livemathtex: format=scientific -->
~~~

Third code block:
```markdown
<!-- livemathtex: output=inplace -->
```

Real directive after code blocks:
<!-- livemathtex: format=engineering -->
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        # Should only have digits=6 from start and format=engineering from end
        assert directives.get('digits') == 6
        assert directives.get('format') == 'engineering'
        assert 'output' not in directives

    def test_directive_outside_code_block_still_works(self):
        """Directives outside code blocks should still be parsed normally."""
        content = '''<!-- livemathtex: digits=4, format=scientific -->

Some text here.

<!-- livemathtex: output=inplace -->
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {'digits': 4, 'format': 'scientific', 'output': 'inplace'}

    def test_code_block_with_language_specifier(self):
        """Code blocks with language specifiers should also be skipped."""
        content = '''<!-- livemathtex: digits=4 -->

```python
# Example: <!-- livemathtex: digits=2 -->
def foo():
    pass
```
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {'digits': 4}

    def test_nested_backticks_in_code_block(self):
        """Content with backticks inside code blocks should be handled."""
        content = '''<!-- livemathtex: digits=6 -->

```markdown
Use `inline code` and:
<!-- livemathtex: digits=1 -->
```
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {'digits': 6}

    def test_empty_document_no_directives(self):
        """Empty document should return empty directives."""
        content = ''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {}

    def test_only_code_block_no_real_directives(self):
        """Document with only code block directives should return empty."""
        content = '''```
<!-- livemathtex: digits=4 -->
```
'''
        lexer = Lexer()
        directives = lexer.parse_document_directives(content)
        assert directives == {}

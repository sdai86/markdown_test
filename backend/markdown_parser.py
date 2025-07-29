import re
import time
from typing import List, Dict, Any, Optional, Tuple
from markdown_it import MarkdownIt
from markdown_it.token import Token
import mistune
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParsedBlock:
    type: str
    content: str
    raw_content: str
    level: int = 0
    order_index: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class MarkdownParser:
    def __init__(self, use_ast: bool = False):
        self.use_ast = use_ast
        self.md = MarkdownIt()
        self.mistune_parser = mistune.create_markdown(renderer=None)
        
    def parse_markdown(self, content: str) -> Tuple[List[ParsedBlock], Dict[str, Any]]:
        """Parse markdown content into blocks with performance logging."""
        start_time = time.time()
        
        if self.use_ast:
            blocks, stats = self._parse_with_ast(content)
        else:
            blocks, stats = self._parse_direct_blocks(content)
            
        parse_time = (time.time() - start_time) * 1000
        stats['parse_time_ms'] = parse_time
        
        logger.info(f"Parsed {len(blocks)} blocks in {parse_time:.2f}ms")
        return blocks, stats
    
    def _parse_with_ast(self, content: str) -> Tuple[List[ParsedBlock], Dict[str, Any]]:
        """Parse using markdown-it AST."""
        tokens = self.md.parse(content)
        blocks = []
        order_index = 0
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == 'heading_open':
                # Find the corresponding heading content and close
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                content_token = tokens[i + 1] if i + 1 < len(tokens) else None
                
                if content_token and content_token.type == 'inline':
                    block = ParsedBlock(
                        type='heading',
                        content=content_token.content,
                        raw_content=f"{'#' * level} {content_token.content}",
                        level=level,
                        order_index=order_index,
                        metadata={'tag': token.tag}
                    )
                    blocks.append(block)
                    order_index += 1
                i += 2  # Skip content and close tokens
                
            elif token.type == 'paragraph_open':
                content_token = tokens[i + 1] if i + 1 < len(tokens) else None
                if content_token and content_token.type == 'inline':
                    block = ParsedBlock(
                        type='paragraph',
                        content=content_token.content,
                        raw_content=content_token.content,
                        order_index=order_index
                    )
                    blocks.append(block)
                    order_index += 1
                i += 2
                
            elif token.type == 'code_block':
                block = ParsedBlock(
                    type='code',
                    content=token.content.rstrip('\n'),
                    raw_content=f"```\n{token.content}```",
                    order_index=order_index,
                    metadata={'language': token.info or 'text'}
                )
                blocks.append(block)
                order_index += 1
                i += 1
                
            elif token.type == 'fence':
                block = ParsedBlock(
                    type='code',
                    content=token.content.rstrip('\n'),
                    raw_content=f"```{token.info or ''}\n{token.content}```",
                    order_index=order_index,
                    metadata={'language': token.info or 'text'}
                )
                blocks.append(block)
                order_index += 1
                i += 1
                
            elif token.type == 'blockquote_open':
                # Collect blockquote content
                quote_content = []
                i += 1
                while i < len(tokens) and tokens[i].type != 'blockquote_close':
                    if tokens[i].type == 'inline':
                        quote_content.append(tokens[i].content)
                    i += 1
                
                content = ' '.join(quote_content)
                block = ParsedBlock(
                    type='blockquote',
                    content=content,
                    raw_content=f"> {content}",
                    order_index=order_index
                )
                blocks.append(block)
                order_index += 1
                i += 1
                
            else:
                i += 1
        
        stats = {
            'total_tokens': len(tokens),
            'method': 'ast'
        }
        
        return blocks, stats

    def _parse_direct_blocks(self, content: str) -> Tuple[List[ParsedBlock], Dict[str, Any]]:
        """Parse markdown directly into blocks without full AST."""
        lines = content.split('\n')
        blocks = []
        order_index = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2)
                block = ParsedBlock(
                    type='heading',
                    content=content,
                    raw_content=line,
                    level=level,
                    order_index=order_index
                )
                blocks.append(block)
                order_index += 1
                i += 1
                continue

            # Code block (fenced)
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip()
                code_lines = []
                i += 1

                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1

                code_content = '\n'.join(code_lines)
                raw_content = f"```{language}\n{code_content}\n```"

                block = ParsedBlock(
                    type='code',
                    content=code_content,
                    raw_content=raw_content,
                    order_index=order_index,
                    metadata={'language': language or 'text'}
                )
                blocks.append(block)
                order_index += 1
                i += 1  # Skip closing ```
                continue

            # Blockquote
            if line.strip().startswith('>'):
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    quote_lines.append(lines[i].strip()[1:].strip())
                    i += 1

                content = ' '.join(quote_lines)
                raw_content = '\n'.join([f"> {line}" for line in quote_lines])

                block = ParsedBlock(
                    type='blockquote',
                    content=content,
                    raw_content=raw_content,
                    order_index=order_index
                )
                blocks.append(block)
                order_index += 1
                continue

            # List items
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                content = list_match.group(3)

                list_type = 'ordered' if marker.endswith('.') else 'unordered'
                level = indent // 2  # Assume 2 spaces per level

                block = ParsedBlock(
                    type='list_item',
                    content=content,
                    raw_content=line,
                    level=level,
                    order_index=order_index,
                    metadata={'list_type': list_type, 'marker': marker}
                )
                blocks.append(block)
                order_index += 1
                i += 1
                continue

            # Regular paragraph
            paragraph_lines = [line]
            i += 1

            # Collect consecutive non-empty lines that aren't special blocks
            while i < len(lines):
                next_line = lines[i]
                if (not next_line.strip() or
                    re.match(r'^#{1,6}\s+', next_line) or
                    next_line.strip().startswith('```') or
                    next_line.strip().startswith('>') or
                    re.match(r'^(\s*)([-*+]|\d+\.)\s+', next_line)):
                    break
                paragraph_lines.append(next_line)
                i += 1

            content = ' '.join(paragraph_lines).strip()
            if content:
                block = ParsedBlock(
                    type='paragraph',
                    content=content,
                    raw_content='\n'.join(paragraph_lines),
                    order_index=order_index
                )
                blocks.append(block)
                order_index += 1

        stats = {
            'total_lines': len(lines),
            'method': 'direct'
        }

        return blocks, stats

    def extract_toc(self, blocks: List[ParsedBlock]) -> List[Dict[str, Any]]:
        """Extract table of contents from heading blocks."""
        toc = []
        for block in blocks:
            if block.type == 'heading':
                toc.append({
                    'text': block.content,
                    'level': block.level,
                    'order_index': block.order_index
                })
        return toc

    def blocks_to_markdown(self, blocks: List[ParsedBlock]) -> str:
        """Convert blocks back to markdown."""
        markdown_lines = []

        for block in blocks:
            if block.type == 'heading':
                markdown_lines.append(f"{'#' * block.level} {block.content}")
            elif block.type == 'paragraph':
                markdown_lines.append(block.content)
            elif block.type == 'code':
                language = block.metadata.get('language', '')
                markdown_lines.append(f"```{language}")
                markdown_lines.append(block.content)
                markdown_lines.append("```")
            elif block.type == 'blockquote':
                for line in block.content.split('\n'):
                    markdown_lines.append(f"> {line}")
            elif block.type == 'list_item':
                indent = '  ' * block.level
                marker = block.metadata.get('marker', '-')
                markdown_lines.append(f"{indent}{marker} {block.content}")

            markdown_lines.append("")  # Add blank line between blocks

        return '\n'.join(markdown_lines)

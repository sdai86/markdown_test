"""
AST Service for parsing and manipulating markdown documents.
Handles conversion between markdown and AST, and AST node operations.
"""

import uuid
import re
from typing import Dict, List, Any, Optional, Tuple
from markdown_it import MarkdownIt
from markdown_it.token import Token


class ASTService:
    def __init__(self):
        # Configure markdown-it with plugins for rich parsing
        self.md = MarkdownIt("commonmark", {
            "html": True,
            "linkify": True,
            "typographer": True
        }).enable([
            'table',
            'strikethrough'
        ])
    
    def parse_markdown_to_ast(self, markdown: str) -> Dict[str, Any]:
        """
        Convert markdown text to AST structure with node IDs.
        
        Args:
            markdown: Raw markdown text
            
        Returns:
            AST dictionary with document structure
        """
        if not markdown.strip():
            return self._create_empty_document()
        
        # Parse markdown to tokens
        tokens = self.md.parse(markdown)
        
        # Convert tokens to AST
        ast = self._tokens_to_ast(tokens)
        
        # Assign unique IDs to all nodes
        self._assign_node_ids(ast)
        
        # Calculate metadata
        metadata = self._calculate_metadata(ast)
        ast["metadata"] = metadata
        
        return ast
    
    def ast_to_markdown(self, ast: Dict[str, Any]) -> str:
        """
        Convert AST back to markdown text.
        
        Args:
            ast: AST dictionary
            
        Returns:
            Markdown text
        """
        if not ast or not ast.get("children"):
            return ""
        
        return self._render_ast_nodes(ast["children"])
    
    def update_ast_node(self, ast: Dict[str, Any], node_id: str, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update specific AST node by ID.
        
        Args:
            ast: Document AST
            node_id: Target node ID
            operation: Operation type (update, insert, delete, move)
            data: Operation data
            
        Returns:
            Updated AST
        """
        ast_copy = self._deep_copy_ast(ast)
        
        if operation == "update":
            self._update_node_content(ast_copy, node_id, data.get("content", ""))
        elif operation == "insert":
            self._insert_node(ast_copy, node_id, data.get("position", "after"), data.get("node"))
        elif operation == "delete":
            self._delete_node(ast_copy, node_id)
        elif operation == "move":
            self._move_node(ast_copy, node_id, data.get("target_id"), data.get("position", "after"))
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Recalculate metadata after changes
        ast_copy["metadata"] = self._calculate_metadata(ast_copy)
        
        return ast_copy
    
    def find_node_by_id(self, ast: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
        """Find a node in the AST by its ID."""
        def search_node(node):
            if node.get("id") == node_id:
                return node
            
            for child in node.get("children", []):
                result = search_node(child)
                if result:
                    return result
            return None
        
        return search_node(ast)
    
    def get_node_path(self, ast: Dict[str, Any], node_id: str) -> List[int]:
        """Get the path to a node in the AST (list of indices)."""
        def find_path(node, path=[]):
            if node.get("id") == node_id:
                return path
            
            for i, child in enumerate(node.get("children", [])):
                result = find_path(child, path + [i])
                if result is not None:
                    return result
            return None
        
        return find_path(ast) or []
    
    def _create_empty_document(self) -> Dict[str, Any]:
        """Create an empty document AST."""
        return {
            "type": "document",
            "children": [],
            "metadata": {
                "wordCount": 0,
                "nodeCount": 0,
                "pageCount": 0
            }
        }
    
    def _tokens_to_ast(self, tokens: List[Token]) -> Dict[str, Any]:
        """Convert markdown-it tokens to AST structure."""
        ast = {
            "type": "document",
            "children": []
        }
        
        stack = [ast]
        
        for token in tokens:
            if token.type.endswith("_open"):
                # Opening tag - create new node
                node = self._token_to_node(token)
                stack[-1]["children"].append(node)
                
                # If this node can have children, push to stack
                if token.type in ["heading_open", "paragraph_open", "list_item_open", 
                                "blockquote_open", "bullet_list_open", "ordered_list_open"]:
                    stack.append(node)
                    
            elif token.type.endswith("_close"):
                # Closing tag - pop from stack
                if len(stack) > 1:
                    stack.pop()
                    
            elif token.type == "inline":
                # Inline content - add to current node
                if stack[-1].get("type") in ["heading", "paragraph", "list_item"]:
                    stack[-1]["content"] = token.content
                    
            else:
                # Self-closing elements
                node = self._token_to_node(token)
                if node:
                    stack[-1]["children"].append(node)
        
        return ast
    
    def _token_to_node(self, token: Token) -> Dict[str, Any]:
        """Convert a markdown-it token to an AST node."""
        node = {
            "type": self._normalize_token_type(token.type),
            "content": getattr(token, 'content', ''),
            "children": []
        }
        
        # Add type-specific attributes
        if token.type.startswith("heading"):
            node["level"] = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
        elif token.type.startswith("list"):
            node["listType"] = "ordered" if token.type.startswith("ordered") else "unordered"
        elif token.type == "fence":
            node["language"] = getattr(token, 'info', '')
        
        # Add position information
        if hasattr(token, 'map') and token.map:
            node["position"] = {
                "line": token.map[0] + 1,
                "column": 1
            }
        
        return node
    
    def _normalize_token_type(self, token_type: str) -> str:
        """Normalize token types to consistent AST node types."""
        type_map = {
            "heading_open": "heading",
            "paragraph_open": "paragraph", 
            "list_item_open": "list_item",
            "bullet_list_open": "list",
            "ordered_list_open": "list",
            "blockquote_open": "blockquote",
            "fence": "code_block",
            "code_inline": "code",
            "hr": "horizontal_rule"
        }
        return type_map.get(token_type, token_type)
    
    def _assign_node_ids(self, ast: Dict[str, Any]) -> None:
        """Recursively assign unique IDs to all AST nodes."""
        def assign_ids(node):
            if "id" not in node:
                node["id"] = f"node_{uuid.uuid4().hex[:8]}"
            
            for child in node.get("children", []):
                assign_ids(child)
        
        assign_ids(ast)
    
    def _calculate_metadata(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate document metadata from AST."""
        word_count = 0
        node_count = 0
        
        def count_nodes(node):
            nonlocal word_count, node_count
            node_count += 1
            
            content = node.get("content", "")
            if content:
                # Simple word count
                words = len(re.findall(r'\b\w+\b', content))
                word_count += words
            
            for child in node.get("children", []):
                count_nodes(child)
        
        for child in ast.get("children", []):
            count_nodes(child)
        
        # Estimate page count (assuming ~250 words per page)
        page_count = max(1, (word_count + 249) // 250)
        
        return {
            "wordCount": word_count,
            "nodeCount": node_count,
            "pageCount": page_count
        }
    
    def _render_ast_nodes(self, nodes: List[Dict[str, Any]], level: int = 0) -> str:
        """Render AST nodes back to markdown."""
        result = []
        
        for node in nodes:
            node_type = node.get("type")
            content = node.get("content", "")
            
            if node_type == "heading":
                level = node.get("level", 1)
                result.append(f"{'#' * level} {content}")
            elif node_type == "paragraph":
                result.append(content)
            elif node_type == "list":
                # Render list items
                for i, child in enumerate(node.get("children", [])):
                    if node.get("listType") == "ordered":
                        result.append(f"{i+1}. {child.get('content', '')}")
                    else:
                        result.append(f"- {child.get('content', '')}")
            elif node_type == "code_block":
                language = node.get("language", "")
                result.append(f"```{language}\n{content}\n```")
            elif node_type == "blockquote":
                lines = content.split('\n')
                quoted = '\n'.join(f"> {line}" for line in lines)
                result.append(quoted)
            elif node_type == "horizontal_rule":
                result.append("---")
            else:
                # Default: just add content
                if content:
                    result.append(content)
            
            # Render children if any
            children_md = self._render_ast_nodes(node.get("children", []), level + 1)
            if children_md:
                result.append(children_md)
        
        return "\n\n".join(result)
    
    def _deep_copy_ast(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of the AST."""
        import copy
        return copy.deepcopy(ast)
    
    def _update_node_content(self, ast: Dict[str, Any], node_id: str, content: str) -> None:
        """Update the content of a specific node."""
        node = self.find_node_by_id(ast, node_id)
        if node:
            node["content"] = content
    
    def _insert_node(self, ast: Dict[str, Any], target_id: str, position: str, new_node: Dict[str, Any]) -> None:
        """Insert a new node relative to target node."""
        # Implementation for inserting nodes
        pass
    
    def _delete_node(self, ast: Dict[str, Any], node_id: str) -> None:
        """Delete a node from the AST."""
        # Implementation for deleting nodes
        pass
    
    def _move_node(self, ast: Dict[str, Any], node_id: str, target_id: str, position: str) -> None:
        """Move a node to a new position."""
        # Implementation for moving nodes
        pass

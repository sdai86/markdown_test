#!/usr/bin/env python3
"""
Script to generate a large sample Markdown file for testing the markdown editor.
This creates a ~300 page document with ~1000+ blocks.
"""

import os
import random
from datetime import datetime

def generate_large_markdown_file(output_path: str, target_blocks: int = 1200):
    """Generate a large markdown file with the specified number of blocks."""
    
    lines = []
    block_count = 0
    
    # Title and introduction
    lines.extend([
        "# The Complete Guide to Software Engineering",
        "",
        "This is a comprehensive guide covering all aspects of modern software engineering.",
        "Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "## Table of Contents",
        "",
        "This document covers the following topics:",
        "",
        "- Software Development Lifecycle",
        "- Programming Languages and Paradigms", 
        "- Database Design and Management",
        "- Web Development Technologies",
        "- DevOps and Deployment",
        "- Testing and Quality Assurance",
        "- Performance Optimization",
        "- Security Best Practices",
        "",
    ])
    block_count += 10
    
    # Generate chapters
    chapters = [
        "Software Development Lifecycle",
        "Programming Languages and Paradigms",
        "Database Design and Management", 
        "Web Development Technologies",
        "DevOps and Deployment",
        "Testing and Quality Assurance",
        "Performance Optimization",
        "Security Best Practices",
        "Project Management",
        "Code Review and Collaboration",
        "Documentation and Communication",
        "Career Development"
    ]
    
    for chapter_num, chapter_title in enumerate(chapters, 1):
        if block_count >= target_blocks:
            break
            
        # Chapter heading
        lines.extend([
            f"# Chapter {chapter_num}: {chapter_title}",
            "",
            f"This chapter covers the essential concepts and practices of {chapter_title.lower()}.",
            ""
        ])
        block_count += 3
        
        # Generate sections within each chapter
        for section_num in range(1, 8):  # 7 sections per chapter
            if block_count >= target_blocks:
                break
                
            section_title = generate_section_title(chapter_title, section_num)
            lines.extend([
                f"## {section_num}. {section_title}",
                "",
            ])
            block_count += 1
            
            # Generate subsections
            for subsection_num in range(1, 5):  # 4 subsections per section
                if block_count >= target_blocks:
                    break
                    
                subsection_title = generate_subsection_title(section_title, subsection_num)
                lines.extend([
                    f"### {section_num}.{subsection_num} {subsection_title}",
                    "",
                ])
                block_count += 1
                
                # Generate content blocks
                content_blocks = random.randint(3, 8)
                for _ in range(content_blocks):
                    if block_count >= target_blocks:
                        break
                        
                    block_type = random.choices(
                        ['paragraph', 'code', 'list', 'blockquote'],
                        weights=[60, 15, 15, 10]
                    )[0]
                    
                    if block_type == 'paragraph':
                        lines.extend([
                            generate_paragraph(subsection_title),
                            ""
                        ])
                        block_count += 1
                        
                    elif block_type == 'code':
                        language = random.choice(['python', 'javascript', 'sql', 'bash', 'yaml'])
                        code_content = generate_code_block(language, subsection_title)
                        lines.extend([
                            f"```{language}",
                            code_content,
                            "```",
                            ""
                        ])
                        block_count += 1
                        
                    elif block_type == 'list':
                        list_items = random.randint(3, 7)
                        for i in range(list_items):
                            lines.append(f"- {generate_list_item(subsection_title, i+1)}")
                        lines.append("")
                        block_count += 1
                        
                    elif block_type == 'blockquote':
                        lines.extend([
                            f"> {generate_quote(subsection_title)}",
                            ""
                        ])
                        block_count += 1
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated markdown file with approximately {block_count} blocks")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print(f"Line count: {len(lines)}")
    
    return block_count

def generate_section_title(chapter_title: str, section_num: int) -> str:
    """Generate a section title based on the chapter."""
    section_templates = {
        "Software Development Lifecycle": [
            "Requirements Gathering", "Design Patterns", "Implementation Strategies",
            "Testing Methodologies", "Deployment Processes", "Maintenance Practices", "Agile Methodologies"
        ],
        "Programming Languages and Paradigms": [
            "Object-Oriented Programming", "Functional Programming", "Procedural Programming",
            "Language Selection Criteria", "Performance Considerations", "Memory Management", "Concurrency Models"
        ],
        "Database Design and Management": [
            "Relational Database Design", "NoSQL Databases", "Query Optimization",
            "Data Modeling", "Indexing Strategies", "Backup and Recovery", "Scaling Strategies"
        ]
    }
    
    default_sections = [
        "Introduction and Overview", "Core Concepts", "Best Practices",
        "Common Patterns", "Tools and Technologies", "Case Studies", "Advanced Topics"
    ]
    
    sections = section_templates.get(chapter_title, default_sections)
    return sections[(section_num - 1) % len(sections)]

def generate_subsection_title(section_title: str, subsection_num: int) -> str:
    """Generate a subsection title."""
    prefixes = ["Understanding", "Implementing", "Optimizing", "Troubleshooting"]
    return f"{prefixes[(subsection_num - 1) % len(prefixes)]} {section_title}"

def generate_paragraph(topic: str) -> str:
    """Generate a realistic paragraph about the topic."""
    templates = [
        f"When working with {topic.lower()}, it's important to consider the various approaches and methodologies available. Each approach has its own advantages and trade-offs that must be carefully evaluated based on the specific requirements of your project.",
        
        f"The implementation of {topic.lower()} requires careful planning and attention to detail. Developers should follow established best practices and patterns to ensure maintainable and scalable solutions.",
        
        f"Modern {topic.lower()} techniques have evolved significantly over the past decade. New tools and frameworks have emerged that simplify complex tasks and improve developer productivity.",
        
        f"Performance considerations are crucial when dealing with {topic.lower()}. Proper optimization techniques can significantly improve system responsiveness and user experience."
    ]
    
    return random.choice(templates)

def generate_code_block(language: str, topic: str) -> str:
    """Generate a code block in the specified language."""
    code_templates = {
        'python': [
            f"def process_{topic.lower().replace(' ', '_')}(data):\n    \"\"\"{topic} processing function\"\"\"\n    result = []\n    for item in data:\n        if validate_item(item):\n            result.append(transform_item(item))\n    return result",
            f"class {topic.replace(' ', '')}Manager:\n    def __init__(self, config):\n        self.config = config\n        self.cache = {{}}\n    \n    def execute(self, params):\n        return self._process_request(params)"
        ],
        'javascript': [
            f"function handle{topic.replace(' ', '')}(data) {{\n  // {topic} handler implementation\n  return data.map(item => {{\n    return {{\n      ...item,\n      processed: true,\n      timestamp: Date.now()\n    }};\n  }});\n}}",
            f"const {topic.lower().replace(' ', '_')}_config = {{\n  timeout: 5000,\n  retries: 3,\n  cache: true,\n  debug: process.env.NODE_ENV === 'development'\n}};"
        ],
        'sql': [
            f"SELECT \n    id,\n    name,\n    created_at,\n    updated_at\nFROM {topic.lower().replace(' ', '_')}_table\nWHERE status = 'active'\nORDER BY created_at DESC\nLIMIT 100;",
            f"CREATE INDEX idx_{topic.lower().replace(' ', '_')}_status \nON {topic.lower().replace(' ', '_')}_table (status, created_at);"
        ]
    }
    
    templates = code_templates.get(language, [f"// {topic} implementation\nconsole.log('Hello, {topic}!');"])
    return random.choice(templates)

def generate_list_item(topic: str, item_num: int) -> str:
    """Generate a list item related to the topic."""
    templates = [
        f"Key principle #{item_num} for {topic.lower()}",
        f"Important consideration when implementing {topic.lower()}",
        f"Best practice for {topic.lower()} optimization",
        f"Common pitfall to avoid in {topic.lower()}"
    ]
    
    return random.choice(templates)

def generate_quote(topic: str) -> str:
    """Generate a relevant quote."""
    quotes = [
        f"The key to successful {topic.lower()} is understanding the underlying principles and applying them consistently.",
        f"In the world of {topic.lower()}, simplicity is the ultimate sophistication.",
        f"Effective {topic.lower()} requires both technical expertise and practical experience.",
        f"The best {topic.lower()} solutions are those that solve real problems elegantly."
    ]
    
    return random.choice(quotes)

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(__file__), "..", "sample_data", "large_sample.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("Generating large sample markdown file...")
    block_count = generate_large_markdown_file(output_file, target_blocks=12000)
    print(f"Sample file generated: {output_file}")
    print(f"Estimated blocks: {block_count}")

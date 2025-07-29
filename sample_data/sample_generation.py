import random
import textwrap

LOREM_WORDS = [
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
    "adipiscing", "elit", "integer", "nec", "odio", "praesent",
    "libero", "sed", "cursus", "ante", "dapibus", "diam"
]

def lorem_paragraph(word_count=100):
    return " ".join(random.choices(LOREM_WORDS, k=word_count)).capitalize() + "."

def generate_table(cols=4, rows=5):
    headers = [f"Col{i+1}" for i in range(cols)]
    rows_data = [
        [f"R{r+1}C{c+1}" for c in range(cols)] for r in range(rows)
    ]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join([" --- " for _ in headers]) + "|")
    lines += ["| " + " | ".join(row) + " |" for row in rows_data]
    return "\n".join(lines)

def generate_mermaid():
    return """```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```"""

def generate_equation():
    return r"""$$
E = mc^2 + \int_{a}^{b} x^2 \,dx
$$"""

def generate_markdown_page(page_num: int, max_heading_depth: int = 3):
    output = []
    output.append(f"# Page {page_num}\n")

    for section in range(1, 4):
        depth = random.randint(1, max_heading_depth)
        output.append(f"{'#' * depth} Section {page_num}.{section}\n")

        # Paragraph
        para = lorem_paragraph(word_count=100)
        output.append(textwrap.fill(para, width=80))
        output.append("")

        # Code block
        output.append("```python")
        for i in range(5):
            output.append(f"print('Section {page_num}.{section}, line {i}')")
        output.append("```")

        # Table
        output.append(generate_table())
        output.append("")

        # Bullet list
        for i in range(5):
            output.append(f"- Bullet item {i+1} in section {page_num}.{section}")
        output.append("")

        # Blockquote
        output.append(f"> This is a quote from section {page_num}.{section}\n")

        # Equation
        output.append(generate_equation())
        output.append("")

        # Mermaid
        output.append(generate_mermaid())
        output.append("")

    return "\n".join(output)

def generate_large_markdown(
    output_path: str,
    pages: int = 300,
    max_heading_depth: int = 4,
    seed: int = 42
):
    random.seed(seed)
    with open(output_path, "w", encoding="utf-8") as f:
        for i in range(1, pages + 1):
            md_page = generate_markdown_page(i, max_heading_depth)
            f.write(md_page + "\n\n")
    print(f"✅ Generated large markdown: {pages} pages → {output_path}")


if __name__ == "__main__":
    generate_large_markdown("dummy_300_pages_detailed.md", pages=300)
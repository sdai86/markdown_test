import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'highlight.js/styles/github.css';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          // Custom components for better styling
          h1: ({ children }: any) => <h1 className="markdown-h1">{children}</h1>,
          h2: ({ children }: any) => <h2 className="markdown-h2">{children}</h2>,
          h3: ({ children }: any) => <h3 className="markdown-h3">{children}</h3>,
          h4: ({ children }: any) => <h4 className="markdown-h4">{children}</h4>,
          h5: ({ children }: any) => <h5 className="markdown-h5">{children}</h5>,
          h6: ({ children }: any) => <h6 className="markdown-h6">{children}</h6>,
          p: ({ children }: any) => <p className="markdown-p">{children}</p>,
          code: ({ inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline ? (
              <pre className="markdown-code-block">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            ) : (
              <code className="markdown-inline-code" {...props}>
                {children}
              </code>
            );
          },
          blockquote: ({ children }: any) => (
            <blockquote className="markdown-blockquote">{children}</blockquote>
          ),
          ul: ({ children }: any) => <ul className="markdown-ul">{children}</ul>,
          ol: ({ children }: any) => <ol className="markdown-ol">{children}</ol>,
          li: ({ children }: any) => <li className="markdown-li">{children}</li>,
          table: ({ children }: any) => (
            <div className="markdown-table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          th: ({ children }: any) => <th className="markdown-th">{children}</th>,
          td: ({ children }: any) => <td className="markdown-td">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;

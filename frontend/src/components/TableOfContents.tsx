import React from 'react';
import { TOCItem } from '../types';

interface TableOfContentsProps {
  items: TOCItem[];
  activeItemId: string | null;
  onItemClick: (item: TOCItem) => void;
}

const TableOfContents: React.FC<TableOfContentsProps> = ({
  items,
  activeItemId,
  onItemClick
}) => {
  if (items.length === 0) {
    return <div className="toc-empty">No headings found</div>;
  }

  return (
    <ul className="toc">
      {items.map((item) => (
        <li
          key={item.id}
          className={`toc-item level-${item.level} ${
            activeItemId === item.id ? 'active' : ''
          }`}
          onClick={() => onItemClick(item)}
          title={item.text}
        >
          {item.text}
        </li>
      ))}
    </ul>
  );
};

export default TableOfContents;

import React from 'react';
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table';
import { extractJsonAndText } from '@/lib/utils';

export default function EnhancedJsonDisplay({ message }) {
  const parseJson = (item) => {
    try {
      return JSON.parse(item);
    } catch (e) {
      return item;
    }
  };

  const renderContent = (content: unknown) => {
    if (Array.isArray(content)) {
      return <JsonTable data={content} />;
    } else if (typeof content === 'object' && content !== null) {
      return <JsonTable data={[content]} />;
    } else {
      return <div>{String(content)}</div>;
    }
  };

  return (
    <div>
      {extractJsonAndText(message.content).map((item, idx) => {
        const parsedItem = parseJson(item);
        return (
          <div key={idx} className="mb-4">
            {renderContent(parsedItem)}
          </div>
        );
      })}
    </div>
  );
}

function JsonTable({ data }: { data: any[] }) {
    if (!Array.isArray(data) || data.length === 0) {
      return null;
    }
    const headers = Array.from(new Set(data.flatMap(obj => Object.keys(obj))));
  
    return (
      <Table className="w-full mt-2">
        <TableHeader>
          <TableRow>
            {headers.map((header) => (
              <TableHead key={header}>{header}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, rowIndex) => (
            <TableRow key={rowIndex}>
              {headers.map((header, cellIndex) => (
                <TableCell key={cellIndex}>
                  {typeof item[header] === 'object'
                    ? JSON.stringify(item[header])
                    : String(item[header] ?? '')}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  };
  
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollBar } from "@/components/ui/scroll-area";
import { Message, roleSchema } from "@/types/actions/query";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import ReactMarkdown from "react-markdown";
import Loader from "react-loaders";
import "loaders.css/src/animations/ball-pulse.scss";
import { Button } from "@/components/ui/button";

type ChatContainerProps = {
  chatHistory: Message[];
  profileImageUrl: string;
  fallbackCharacter: string;
  isResponseFetching: boolean;
  updateChatHistory: (newChatHistory: Message[]) => void;
};

export default function ChatContainer({
  chatHistory,
  profileImageUrl,
  fallbackCharacter,
  isResponseFetching,
  updateChatHistory
}: ChatContainerProps) {

  const handleDelete = (index: number) => {
    updateChatHistory(chatHistory.filter((_, i) => i < index));
  };

  return (
    <div>
      {chatHistory.map((message: Message, index: number) => (
        // eslint-disable-next-line react/no-array-index-key
        <div key={index}>
          <div
            className={`flex items-start mb-4 ${
              message.role === roleSchema.Values.user
                ? "justify-end"
                : "justify-start"
            }`}
          >
            {message.role === roleSchema.Values.assistant && (
              <Avatar className="mr-2">
                <AvatarImage src="/path/to/assistant-avatar.png" />
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
            )}
            <div
              className={`relative p-4 rounded-lg ${
                message.role === roleSchema.Values.user
                  ? "bg-blue-500 dark:bg-blue-800 text-white"
                  : "bg-gray-300 dark:bg-gray-400 text-black"
              }`}
            >
              {
                message.role === roleSchema.Values.user && 
                <Button
                  className="absolute top-2 right-2 bg-transparent border-none p-0 size-2 text-white hover:bg-transparent"
                  onClick={() => handleDelete(index)}
                >
                  x
                </Button>
              }
              <ReactMarkdown
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} className="text-blue-500 underline" />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              {message.data && (
                <div className="relative mt-2 w-full max-w-screen-lg overflow-auto">
                  <Table className="w-full">
                    <TableHeader>
                      <TableRow>
                        {Object.keys(message.data[0]).map((key) => (
                          <TableHead
                            key={key}
                            className="text-left text-gray-500 font-normal text-sm px-4 py-2 whitespace-nowrap"
                          >
                            {key.toLowerCase()}
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {message.data.map((row, rowIndex) => (
                        <TableRow key={rowIndex}>
                          {Object.values(row).map((value, cellIndex) => (
                            <TableCell
                              key={cellIndex}
                              className="px-4 py-2 whitespace-nowrap"
                            >
                              <ReactMarkdown
                                components={{
                                  a: ({ node, ...props }) => (
                                    <a
                                      {...props}
                                      className="text-blue-500 underline"
                                    />
                                  ),
                                }}
                              >
                                {typeof value === "object"
                                  ? JSON.stringify(value)
                                  : String(value)}
                              </ReactMarkdown>
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <ScrollBar orientation="horizontal" />
                </div>
              )}
            </div>
            {message.role === roleSchema.Values.user && (
              <Avatar className="ml-2">
                <AvatarImage src={profileImageUrl} />
                <AvatarFallback>{fallbackCharacter}</AvatarFallback>
              </Avatar>
            )}
          </div>
        </div>
      ))}
      {isResponseFetching && (
        <div className="flex items-start mb-4 justify-start">
          <Avatar className="mr-2">
            <AvatarImage src="/path/to/assistant-avatar.png" />
            <AvatarFallback>AI</AvatarFallback>
          </Avatar>
          <div className="p-2 rounded-lg bg-gray-300 text-black">
            <Loader type="ball-pulse" active={true} />
          </div>
        </div>
      )}
    </div>
  );
}

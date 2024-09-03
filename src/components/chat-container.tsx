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
} from "@/components/ui/table"


type ChatContainerProps = {
  chatHistory: Message[];
  profileImageUrl: string;
  fallbackCharacter: string;
};

export default function ChatContainer({
  chatHistory,
  profileImageUrl,
  fallbackCharacter,
}: ChatContainerProps) {
  return (
    <div>
      {chatHistory.map((message: Message, index: number) => (
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
              className={`p-2 rounded-lg ${
                message.role === roleSchema.Values.user
                  ? "bg-blue-500 text-white"
                  : "bg-gray-300 text-black"
              }`}
            >
              {message.content}
              {message.data && (
                <div className="relative mt-2 w-full max-w-screen-xl overflow-auto">
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
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
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
    </div>
  );
}

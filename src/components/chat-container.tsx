import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Message, roleSchema } from "@/types/actions/query";

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
    <>
      {chatHistory.map((message: Message, index: number) => (
        <div
          key={index}
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
          </div>
          {message.role === roleSchema.Values.user && (
            <Avatar className="ml-2">
              <AvatarImage src={profileImageUrl} />
              <AvatarFallback>{fallbackCharacter}</AvatarFallback>
            </Avatar>
          )}
        </div>
      ))}
    </>
  );
}

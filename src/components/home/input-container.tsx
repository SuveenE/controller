import Loader from "@/components/accessory/loader";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useEffect, useState } from "react";

type InputContainerProps = {
  isButtonDisabled: boolean;
  isResponseFetching: boolean;
  sendMessage: (inputText: string) => void;
};

export default function InputContainer({
  isButtonDisabled,
  isResponseFetching,
  sendMessage,
}: InputContainerProps) {
  const [inputText, setInputText] = useState<string>("");

  const handleSendMessage = () => {
    const trimmedInputText: string = inputText.trim();
    setInputText("");
    sendMessage(trimmedInputText);
  }

  useEffect(() => {
    const handleKeyDown = async (event: KeyboardEvent) => {
      if (
        event.key === "Enter" &&
        document.activeElement?.id === "input-text-area"
      ) {
        event.preventDefault();
        handleSendMessage();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [inputText]);

  return (
    <>
      <Textarea
        id="input-text-area"
        className="border-2 rounded resize-none max-h-[300px] overflow-auto"
        value={inputText}
        disabled={isResponseFetching}
        rows={1}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = "auto";
          target.style.height = `${target.scrollHeight}px`;
        }}
        onChange={(e) => setInputText(e.target.value)}
      />
      {isResponseFetching && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader />
        </div>
      )}
      <Button
        id="send-btn"
        disabled={!inputText || !inputText.trim() || isResponseFetching || isButtonDisabled}
        onClick={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
      >
        Send
      </Button>
    </>
  );
}

"use client";
import { login } from "@/actions/user/login";
import { ScrollArea } from "@/components/ui/scroll-area";
import { API_KEY_QUERY_KEY } from "@/constants/keys";
import { loginRequestSchema } from "@/types/actions/user/login";
import { Integration, integrationEnum } from "@/types/integration";
import { useUser } from "@clerk/nextjs";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import IntegrationIcon from "@/components/home/integration-icon";
import ChatContainer from "@/components/chat-container";
import InputContainer from "@/components/home/input-container";
import {
  Message,
  messageSchema,
  queryRequestSchema,
  queryResponseSchema,
  roleSchema,
} from "@/types/actions/query";
import { toast } from "@/components/ui/use-toast";
import { query } from "@/actions/query";
import { useIntegrationsStore } from "@/types/store/integrations";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const { user, isLoaded } = useUser();
  const { data: apiKey = "", isLoading: isApiKeyLoading } = useQuery({
    queryKey: [API_KEY_QUERY_KEY, user?.id],
    queryFn: async () => {
      if (!isLoaded || !user) {
        return "";
      }
      const parsedLoginRequest = loginRequestSchema.parse({
        id: user.id,
        name: user.firstName,
        email: user.primaryEmailAddress?.emailAddress,
      });
      const response = await login(parsedLoginRequest);

      return response.api_key;
    },
    enabled: isLoaded && !!user,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [instance, setInstance] = useState<string | null>(null);
  const sendMessage = useMutation({
    mutationFn: async (inputText: string): Promise<Message[]> => {
      if (integrationsState.integrations.length === 0) {
        toast({
          title: "Select an integration",
          description:
            "At least one integration must be selected on the left sidebar before sending a message",
          duration: 3000,
        });
        return chatHistory;
      }

      const message = messageSchema.parse({
        role: roleSchema.Values.user,
        content: inputText,
        data: null,
      });
      setChatHistory([...chatHistory, message]);

      const parsedQueryRequest = queryRequestSchema.parse({
        message: message,
        chat_history: chatHistory,
        api_key: apiKey,
        integrations: integrationsState.integrations,
        instance: instance,
      });

      const response = await query(parsedQueryRequest);
      const parsedQueryResponse = queryResponseSchema.parse(response);
      setInstance(parsedQueryResponse.instance);
      return parsedQueryResponse.chat_history;
    },
    onSuccess: (newChatHistory: Message[]) => {
      setChatHistory(newChatHistory);
    },
  });

  const { integrationsState, setIntegrationsState } = useIntegrationsStore();
  const [profileImageUrl, setProfileImageUrl] = useState<string>("");
  const isInitializedRef = useRef(false);

  const clickIntegration = async (integration: Integration) => {
    if (integrationsState.integrations.includes(integration)) {
      setIntegrationsState({
        integrations: integrationsState.integrations.filter(
          (i) => i !== integration,
        ),
      });
    } else {
      setIntegrationsState({
        integrations: [...integrationsState.integrations, integration],
      });
    }
  };

  const removeIntegration = (integration: Integration) => {
    setIntegrationsState({
      integrations: integrationsState.integrations.filter(
        (i) => i !== integration,
      ),
    });
  };

  const integrationIcons = Object.values(integrationEnum.Values).map(
    (integration) => (
      <IntegrationIcon
        key={`${integration}_icon`}
        integration={integration as Integration}
        isHighlighted={integrationsState.integrations.includes(
          integration as Integration,
        )}
        apiKey={apiKey ?? ""}
        clickIntegration={clickIntegration}
        removeIntegration={removeIntegration}
      />
    ),
  );

  useEffect(() => {
    const initializeUser = async () => {
      if (isLoaded && user && !isInitializedRef.current) {
        const googleAccount = user?.externalAccounts.find(
          (account) => account.provider === "google",
        );
        const imageUrl = googleAccount?.imageUrl || user.imageUrl;
        setProfileImageUrl(imageUrl);
        isInitializedRef.current = true;
      }
    };

    initializeUser();
  }, [isLoaded, user]);

  return (
    <div className="flex flex-row h-[calc(100vh-150px)] justify-center">
      <div className="w-[150px]">
        <ScrollArea className="scroll-area h-full">
          {integrationIcons}
        </ScrollArea>
      </div>
      <div className="mx-4 w-full max-w-[calc(100%-200px)] flex flex-col justify-between">
        <ScrollArea className="scroll-area flex-grow relative">
          <Button
            className="absolute top-2 left-2 z-10 text-xs h-6 bg-opacity-20 backdrop-blur transition-none hover:bg-opacity-50 hover:opacity-100"
            onClick={() => {
              setChatHistory([]);
              setInstance(null);
            }}
          >
            CLEAR
          </Button>
          <ChatContainer
            chatHistory={chatHistory}
            profileImageUrl={profileImageUrl}
            fallbackCharacter={user?.firstName?.charAt(0) || "U"}
            isResponseFetching={sendMessage.status === "pending"}
          />
        </ScrollArea>
        <div className="flex mt-5 space-x-2 items-end relative">
          <InputContainer
            isButtonDisabled={isApiKeyLoading}
            isResponseFetching={sendMessage.status === "pending"}
            sendMessage={(inputText: string) => sendMessage.mutate(inputText)}
          />
        </div>
      </div>
    </div>
  );
}

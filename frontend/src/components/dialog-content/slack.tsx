import { AuthParamProps } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";

export default function SlackAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name="Slack"
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="channels:read,chat:write,users:read"
    />
  );
}

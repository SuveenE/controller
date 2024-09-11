import { AuthParamProps } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";

export default function XAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name="X"
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      // scope="tweet.read,tweet.write,users.read,follows.read,follows.write,offline.access"
      scope="tweet.read offline.access"
    />
  );
}

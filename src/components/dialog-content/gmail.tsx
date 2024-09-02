import { AuthParamProps } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";

export default function GmailAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name="Gmail"
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="https://mail.google.com/"
    />
  );
}

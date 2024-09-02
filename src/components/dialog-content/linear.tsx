import { AuthParamProps } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth-base";

export default function LinearAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name="Linear"
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      // scope="read,write,issues:create,comments:create,timeSchedule:write" // Full available scope, but timeSchedule:write bugs out oauth 2 token change for some reason
      scope="read,write,issues:create,comments:create"
    />
  );
}

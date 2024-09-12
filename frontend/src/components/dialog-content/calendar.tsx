import { AuthParamProps } from "@/types/integration";
import AuthDialogContent from "@/components/dialog-content/auth";

export default function GoogleCalendarAuthDialogContent({
  apiKey,
  loginBase,
  exchangeBase,
}: AuthParamProps) {
  return (
    <AuthDialogContent
      name="Calendar"
      apiKey={apiKey}
      loginBase={loginBase}
      exchangeBase={exchangeBase}
      scope="https://www.googleapis.com/auth/calendar"
    />
  );
}

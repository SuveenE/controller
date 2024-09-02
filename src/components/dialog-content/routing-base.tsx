import { Integration, integrationEnum } from "@/types/integration";
import GmailAuthDialogContent from "@/components/dialog-content/gmail";
import GoogleCalendarAuthDialogContent from "@/components/dialog-content/calendar";
import LinearAuthDialogContent from "@/components/dialog-content/linear";
import SlackAuthDialogContent from "@/components/dialog-content/slack";

type RoutingAuthDialogContentProps = {
  apiKey: string;
  integration: Integration;
};

export default function RoutingAuthDialogContent({
  apiKey,
  integration,
}: RoutingAuthDialogContentProps) {
  let dialogContent = null;
  switch (integration) {
    case integrationEnum.Values.gmail:
      dialogContent = (
        <GmailAuthDialogContent
          apiKey={apiKey}
          loginBase="https://accounts.google.com/o/oauth2/v2/auth"
          exchangeBase="https://oauth2.googleapis.com/token"
        />
      );
      break;
    case integrationEnum.Values.calendar:
      dialogContent = (
        <GoogleCalendarAuthDialogContent
          apiKey={apiKey}
          loginBase="https://accounts.google.com/o/oauth2/v2/auth"
          exchangeBase="https://oauth2.googleapis.com/token"
        />
      );
      break;
    case integrationEnum.Values.linear:
      dialogContent = (
        <LinearAuthDialogContent
          apiKey={apiKey}
          loginBase="https://linear.app/oauth/authorize"
          exchangeBase="https://api.linear.app/oauth/token"
        />
      );
      break;
    case integrationEnum.Values.slack:
      dialogContent = (
        <SlackAuthDialogContent
          apiKey={apiKey}
          loginBase="https://slack.com/oauth/v2/authorize"
          exchangeBase="https://slack.com/api/oauth.v2.access"
        />
      );
  }
  return dialogContent;
}
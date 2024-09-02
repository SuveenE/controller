import { z } from "zod";
import { IconType } from "react-icons/lib";
import { BiLogoGmail } from "react-icons/bi";
import { SiGooglecalendar, SiSlack } from "react-icons/si";
import { SiLinear } from "react-icons/si";

export const integrationEnum = z.enum(["gmail", "calendar", "linear", "slack"]);
export type Integration = z.infer<typeof integrationEnum>;
export const integrationsStateSchema = z.object({
  integrations: z.array(integrationEnum),
})
export type IntegrationsState = z.infer<typeof integrationsStateSchema>;
export const defaultIntegrationsState: IntegrationsState = {
  integrations: [],
};

const integrationIconMappingSchema = z.record(
  integrationEnum,
  z.custom<IconType>(),
);
type IntegrationIconMapping = z.infer<typeof integrationIconMappingSchema>;

export const integrationIconMapping: IntegrationIconMapping = {
  gmail: BiLogoGmail,
  calendar: SiGooglecalendar,
  linear: SiLinear,
  slack: SiSlack,
};

export type AuthParamProps = {
  apiKey: string;
  loginBase: string;
  exchangeBase: string;
};

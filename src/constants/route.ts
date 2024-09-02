import type { Route } from "next";

export const ROUTE: Record<string, URL | Route<string>> = {
  home: "/",
  chat: "/chat",
  docs: process.env.NEXT_PUBLIC_DOCS_URL as string,
};

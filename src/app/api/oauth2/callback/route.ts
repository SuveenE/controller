import axios from "axios";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { tokenPostRequestSchema } from "@/types/api/token";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const state = searchParams.get("state");
  const storedState = cookies().get("authState")?.value;
  const storedClientId = cookies().get("clientId")?.value;
  const storedClientSecret = cookies().get("clientSecret")?.value;
  const storedExpandApiKey = cookies().get("expandApiKey")?.value;
  const storedExchangeBase = cookies().get("exchangeBase")?.value || "";
  const storedTableName = cookies().get("tableName")?.value;

  if (!state || state !== storedState) {
    return NextResponse.json(
      { error: "Invalid state parameter" },
      { status: 400 },
    );
  }

  cookies().delete("authState");

  const code = searchParams.get("code");

  if (!code) {
    return NextResponse.json(
      { error: "Authorization code is missing" },
      { status: 400 },
    );
  }

  try {
    const params = new URLSearchParams();

    params.append("client_id", storedClientId as string);
    params.append("client_secret", storedClientSecret as string);
    params.append("code", code);
    params.append(
      "redirect_uri",
      `${process.env.NEXT_PUBLIC_DEFAULT_SITE_URL}/api/oauth2/callback`,
    );
    params.append("grant_type", "authorization_code");
    const response = await axios.post(storedExchangeBase, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    const tokenData = response.data;
    const accessToken: string = tokenData.access_token;
    const refreshToken: string | null = tokenData.refresh_token || null;

    const parsedTokenRequest = tokenPostRequestSchema.parse({
      api_key: storedExpandApiKey,
      access_token: accessToken,
      refresh_token: refreshToken,
      client_id: storedClientId,
      client_secret: storedClientSecret,
      table_name: storedTableName,
    });

    await axios.post(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/token`,
      parsedTokenRequest,
    );

    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_DEFAULT_SITE_URL}`);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to retrieve access token" },
      { status: 500 },
    );
  }
}

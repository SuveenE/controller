import { NextRequest, NextResponse } from "next/server";
import { v4 as uuidv4 } from "uuid";
import { cookies } from "next/headers";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const clientId = searchParams.get("clientId");

  // When Google redirects back to your callback URL with an authorization code, you use both the client ID and client secret to exchange this code for access and refresh tokens.
  const clientSecret = searchParams.get("clientSecret");

  // We need the apiKey of the user so that we know which user to associate the access token and refresh token with
  const expandApiKey = searchParams.get("expandApiKey") || "";

  // We need to know which scopes the user has authorized
  const scope = searchParams.get("scope") || "";

  // We need to know which table to POST the tokens to
  const tableName = searchParams.get("tableName") || "";

  // We need to know which is the base url of the specific integration we are initiating login with
  const loginBase = searchParams.get("loginBase") || "";

  // We need to know which is the base url of the specific integration we are initiating token exchange with
  const exchangeBase = searchParams.get("exchangeBase") || "";

  const code_challenge = searchParams.get("code_challenge") || "";
  const code_challenge_method = searchParams.get("code_challenge_method") || "";
  const redirect_uri = searchParams.get("redirect_uri") || "";

  if (!clientId || !clientSecret) {
    return NextResponse.json(
      { error: "Client ID and Client Secret are required" },
      { status: 400 },
    );
  }

  const state = uuidv4();
  cookies().set("authState", state, { httpOnly: true, secure: true });
  cookies().set("clientId", clientId, { httpOnly: true, secure: true });
  cookies().set("clientSecret", clientSecret, { httpOnly: true, secure: true });
  cookies().set("expandApiKey", expandApiKey, { httpOnly: true, secure: true });
  cookies().set("tableName", tableName, { httpOnly: true, secure: true });
  cookies().set("exchangeBase", exchangeBase, { httpOnly: true, secure: true });
  cookies().set("redirect_uri", redirect_uri, { httpOnly: true, secure: true });

  const authUrl = new URL(loginBase);
  authUrl.searchParams.append("response_type", "code");
  authUrl.searchParams.append("client_id", clientId);
  authUrl.searchParams.append("redirect_uri", redirect_uri);
  authUrl.searchParams.append("scope", scope);
  authUrl.searchParams.append("state", state);
  authUrl.searchParams.append("access_type", "offline");
  authUrl.searchParams.append("prompt", "consent");
  authUrl.searchParams.append("code_challenge", code_challenge);
  authUrl.searchParams.append("code_challenge_method", code_challenge_method);
  console.log(authUrl);
  return NextResponse.redirect('https://twitter.com/i/oauth2/authorize?response_type=code&client_id=aW0tWnUzbXpwMEFtYTI5bTh6TkY6MTpjaQ&redirect_uri=https%3A%2F%2Fexpand-frontend.vercel.app%2Fapi%2Foauth2%2Fcallback&scope=tweet.read&state=state&access_type=offline&prompt=consent&code_challenge=challenge&code_challenge_method=plain');
  // return NextResponse.redirect("https://twitter.com/i/oauth2/authorize?response_type=code&client_id=cFo1S1g4azUweVJzWFBBcEx1LVE6MTpjaQ&redirect_uri=https%3A%2F%2Fvotacionya.000webhostapp.com%2Fcallback%2Flogintwitter.php&scope=tweet.read&state=state&code_challenge=challenge&code_challenge_method=plain");
}

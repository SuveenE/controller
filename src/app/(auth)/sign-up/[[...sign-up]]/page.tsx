"use client";

import { dark } from "@clerk/themes";
import { useTheme } from "next-themes";
import { SignUp } from "@clerk/nextjs";

const SignUpPage = () => {
  const { resolvedTheme } = useTheme();

  return (
    <SignUp
      signInUrl="/sign-in"
      appearance={{
        baseTheme: resolvedTheme === "dark" ? dark : undefined,
      }}
    />
  );
};

export default SignUpPage;

import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <main className="flex justify-center py-10">
      <SignIn fallbackRedirectUrl="/?auto=1" signUpUrl="/sign-up" />
    </main>
  );
}

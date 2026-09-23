import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <main className="flex justify-center py-10">
      <SignUp fallbackRedirectUrl="/?auto=1" signInUrl="/sign-in" />
    </main>
  );
}

<script lang="ts">
  import { goto } from "$app/navigation";
  import { base } from "$app/paths";
  import { logIn, signUp } from "$lib/stores/authStore";
  import type { User, UserCredential } from "firebase/auth";

  type FormType = "log-in" | "sign-up";

  export let formType: FormType;

  let firstName: string = "";
  let lastName: string = "";
  let email: string = "";
  let password: string = "";
  let error: string = "";

  async function onLogIn(e: SubmitEvent) {
    if (!email || !password) {
      error = "Invalid email or password";
      return;
    }

    try {
      await logIn(email, password);
      goto("/classes");
    } catch (e) {
      const code = (e as any).code;

      if (code === "auth/email-already-in-use") {
        await logIn(email, password);
        await goto("/");
        return;
      }

      if (code === "auth/invalid-email") {
        error = "Invalid email";
        return;
      }

      error = "Something went wrong";
      return;
    }
  }

  async function onSignUp() {
    if (!email.trim() || !password.trim()) {
      error = "Invalid input(s)";
      return;
    }

    let credentials: UserCredential;

    try {
      credentials = await signUp(email, password, firstName, lastName);
      goto("/new-class");
    } catch (e) {
      const code = (e as any).code;

      if (code === "auth/email-already-in-use") {
        error = "Email already exists";
        return;
      }

      if (code === "auth/invalid-email") {
        error = "Invalid email";
        return;
      }

      if (code === "auth/weak-password") {
        error = "Password should be at least 6 characters";
        return;
      }

      error = "Something went wrong";
      return;
    }
  }
</script>

<form
  class="auth-form items-center w-full"
  on:submit|preventDefault={formType === "log-in" ? onLogIn : onSignUp}
>
  {#if formType === "sign-up"}
    <div class="name-control flex justify-between gap-[10%] w-full">
      <div class="form-control w-1/2">
        <label for="first-name" class="font-bold">First Name</label>
        <input
          bind:value={firstName}
          required
          type="text"
          name="first-name"
          id="first-name"
          placeholder="First Name"
        />
      </div>
      <div class="form-control w-1/2">
        <label for="last-name">Last Name</label>
        <input
          bind:value={lastName}
          required
          type="text"
          name="last-name"
          id="last-name"
          placeholder="Last Name"
        />
      </div>
    </div>
  {/if}
  <div class="form-control">
    <label for="email">Email</label>
    <input
      required
      type="email"
      name="email"
      id="email"
      placeholder="Email"
      bind:value={email}
    />
  </div>
  <div class="form-control">
    <label for="password">Password</label>
    <input
      required
      type="password"
      name="password"
      id="password"
      placeholder="Password"
      bind:value={password}
    />
  </div>
  {#if error}
    <p class="text-[#b64040]">{error}</p>
  {/if}
  {#if formType === "sign-up"}
    <p>
      Already have an account? <a
        class="font-bold hover:underline"
        href="{base}/log-in">Log in</a
      >
    </p>
  {/if}
  <button
    class="w-full bg-accent rounded-lg py-2 mt-2 text-white hover:translate-y-1 transition-transform"
    type="submit">{formType === "log-in" ? "Log In" : "Sign Up"}</button
  >
</form>

<style lang="scss">
  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    @apply font-bold block text-black w-full mb-[2px];
  }
  .form-control > input {
    @apply bg-light-accent rounded-md outline-none p-2 w-full placeholder-black;
  }

  .form-control > input:focus {
    @apply shadow-inner;
  }

  .form-control,
  .name-control {
    width: min(60vw, 30rem);
  }
</style>

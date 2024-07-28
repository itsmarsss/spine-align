<script lang="ts">
  	import { goto } from "$app/navigation";
	import { logIn, signUp } from "$lib/stores/authStore";
	import type { UserCredential } from "firebase/auth";

	type FormType = "log-in" | "sign-up";

	export let formType: FormType;

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
			goto("/classes")
		} catch (e) {
			const code = (e as any).code;

			if (code === "auth/email-already-in-use") {
				await logIn(email, password);
				await goto("/");
				return;
			} 

			if (code === "auth/invalid-email") {
				error = "Invalid email"
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
			credentials = await signUp(email, password);
		} catch (e) {
			const code = (e as any).code;

			if (code === "auth/email-already-in-use") {
				error = "Email already exists"
				return;
			} 

			if (code === "auth/invalid-email") {
				error = "Invalid email"
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

<form class="auth-form" on:submit={formType === "log-in" ? onLogIn : onSignUp}>
	<!-- <div class="name-control">
		<div class="form-control">
			<label for="first-name">First Name</label>
			<input type="text" name="first-name" id="first-name">
		</div>
		<div class="form-control">
			<label for="last-name">Last Name</label>
			<input type="text" name="last-name" id="last-name">
		</div>
	</div> -->
	<div class="form-control">
		<label for="email">Email</label>
		<input type="email" name="email" id="email" bind:value={email}>
	</div>
	<div class="form-control">
		<label for="password">Password</label>
		<input type="password" name="password" id="password" bind:value={password}>
	</div>
	<p>{error ?? ""}</p>
	<div class="submit-group">
		<button type="submit">{formType === "log-in" ? "Log In" : "Sign Up"}</button>
	</div>
</form>

<style lang="scss">
	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
</style>
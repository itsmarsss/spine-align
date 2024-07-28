<script lang="ts">
	import AuthForm from "$lib/components/AuthForm.svelte";

</script>

<svelte:head>
	<title>Sign Up | Spine Align</title>
</svelte:head>
<main class="w-screen size flex flex-col items-center justify-center">
	<div class="w-fit">
		<h1 class="text-3xl mb-4">
			Sign <span class="text-accent">Up</span>
		</h1>
		<AuthForm formType={"sign-up"}/>
	</div>
</main>

<style>
	.size {
		height: calc(100vh - 5rem);
	}
</style>
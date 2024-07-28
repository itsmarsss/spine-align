<script lang="ts">
	import AuthForm from "$lib/components/AuthForm.svelte";
</script>

<svelte:head>
	<title>Log In | Spine Align</title>
</svelte:head>
<div class="w-screen size flex flex-col items-center justify-center">
	<div class="w-fit">
		<h1 class="text-3xl mb-4">
			Log <span class="text-accent">In</span>
		</h1>
		<AuthForm formType={"log-in"}/>
	</div>
</div>

<style>
	.size {
		height: calc(100vh - 5rem);
	}
</style>
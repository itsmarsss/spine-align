<script lang="ts">
	import { onMount } from "svelte";
	import { firebaseAuth } from "$lib/firebase";
	import authStore from "$lib/stores/authStore";
	import { browser } from "$app/environment";
	import { goto } from "$app/navigation";
	import "./index.css";
  	import NavBar from "$lib/components/NavBar.svelte";

	const AUTHENTICATED_ROUTES = [
		"/classes",
		"/new-class",
	]

	onMount(() => {
		const unsubscribe = firebaseAuth.onAuthStateChanged((user) => {
			authStore.set(user)


			if (browser && AUTHENTICATED_ROUTES.some(route => window.location.pathname.startsWith(route)) && !$authStore) {
				goto("/log-in");
			}
		});
	
		return unsubscribe;
	})
</script>

<!-- landing page -->
<header class="w-screen">
    <NavBar/>
</header>

<slot/>
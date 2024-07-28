<script lang="ts">
	import type { PageServerData } from "./$types"
	import VideoPlayer from "$lib/components/VideoPlayer.svelte";
	import authStore from "$lib/stores/authStore";
	import { firestore } from "$lib/firebase"
	import { doc, getDoc } from "firebase/firestore";
  import { goto } from "$app/navigation";

	export let data: PageServerData;

	authStore.subscribe(async user => {

		if (!user) {
			return;
		}

		const docRef = doc(firestore, "classes", data.id);

		const docData = await getDoc(docRef);

	 	if (!docData.exists() || docData.get("userID") !== user.uid) {
			goto("/classes")
		}
	})
</script>

<main>
	<div class="size">
		<VideoPlayer classId={data.id}/>
	</div>
</main>

<style lang="scss">
	.size {
		margin: 1rem auto;
		width: max(30rem, calc(80% * 9 / 16 + 4rem));
	}
</style>
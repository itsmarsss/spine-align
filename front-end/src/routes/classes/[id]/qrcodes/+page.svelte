<script lang="ts">
	import type { PageServerData } from "./$types"
	import VideoPlayer from "$lib/components/VideoPlayer.svelte";
	import authStore from "$lib/stores/authStore";
	import { firestore } from "$lib/firebase"
	import { doc, getDoc } from "firebase/firestore";
  	import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { createQrSvgDataUrl, createQrSvgString } from "@svelte-put/qr";

	export let data: PageServerData;

	let qrCodes: {
		dataURL: string;
		svgString: string;
	}[]

	authStore.subscribe(async user => {
		if (!user) {
			return;
		}

		const docRef = doc(firestore, "classes", data.id);

		const docData = await getDoc(docRef);

	 	if (!docData.exists() || docData.get("userID") !== user.uid) {
			goto("/classes")
		}

		const positions = docData.get("positions") as Record<string, [number, number]>[];

		qrCodes = Object.entries(positions)
			.map((_, i) => createQRCode(`api/poll/${data.id}/${i}`))
	})

	function createQRCode(url: string) {
		const path = $page.url.host
		const config = { data: `${path}/${url}` }

		const dataURL = createQrSvgDataUrl(config);
		const svgString = createQrSvgString(config);

		return {
			dataURL,
			svgString,
		}
	}
</script>

<main class="clamp-width mx-auto my-2 grid grid-cols-8 gap-4">
	{#if qrCodes} 
		{#each qrCodes as { dataURL, svgString }, i}
			<div class="flex flex-col gap-1">
				<a href={dataURL} download="qr_{i + 1}.svg">{@html svgString}</a>
				<p class="text-center">QR Code {i + 1}</p>
			</div> 
		{/each}
	{:else}
		<p class="bg-center">Generating QR Codes...</p>
	{/if}
</main>

<style lang="scss">
	.clamp-width {
		width: clamp(16rem, 80%, 84rem);
	}

	.size {
		margin: 1rem auto;
		width: max(30rem, calc(80% * 9 / 16 + 4rem));
	}
</style>
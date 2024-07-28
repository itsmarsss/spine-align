<script lang="ts">
  	import type { Point } from "$lib/models/classes";
  	import authStore from "$lib/stores/authStore";
  	import { createEventDispatcher } from "svelte";

	let videoElement: HTMLVideoElement;

	const eventDispatcher = createEventDispatcher<{"video-play": {width: number, height: number}}>();

	authStore.subscribe(async (user) => {
		if (!user) {
			return;
		}

		const mediaStream = await navigator.mediaDevices.getUserMedia({
			video: true,
			audio: true,
		});

		videoElement.srcObject = mediaStream;
		await videoElement.play();

		eventDispatcher("video-play", {
			width: videoElement.offsetWidth,
			height: videoElement.offsetHeight,
		})
	})
</script>

<section>
	<!-- svelte-ignore a11y-media-has-caption -->
	<video bind:this={videoElement}></video>
</section>
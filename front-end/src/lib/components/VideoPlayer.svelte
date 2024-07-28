<script lang="ts">
  	import authStore from "$lib/stores/authStore";
  	import { createEventDispatcher } from "svelte";
  	import Window from "$lib/components/Window.svelte";

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

<Window>
	<!-- svelte-ignore a11y-media-has-caption -->
	<video bind:this={videoElement} class="w-full aspect-[4/3]"></video>
</Window>


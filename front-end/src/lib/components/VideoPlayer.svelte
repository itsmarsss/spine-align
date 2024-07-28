<script lang="ts">
  	import authStore from "$lib/stores/authStore";
  	import { createEventDispatcher, onDestroy, onMount } from "svelte";
  	import Window from "$lib/components/Window.svelte";
	import { doc, getDoc } from "firebase/firestore";
	import { firestore } from "$lib/firebase";
	import { goto } from "$app/navigation";

	export let classId: string | null;

	let positions: Record<string, [number, number]>;

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;

	const eventDispatcher = createEventDispatcher<{"video-play": {width: number, height: number}}>();

	authStore.subscribe(async (user) => {
		if (!user) {
			return;
		}

		const mediaStream = await navigator.mediaDevices.getUserMedia({
			video: true,
			audio: false,
		});

		videoElement.srcObject = mediaStream;
		await videoElement.play();

		eventDispatcher("video-play", {
			width: videoElement.offsetWidth,
			height: videoElement.offsetHeight,
		});

		if (!classId) {
			return;
		}

		const docRef = doc(firestore, "classes", classId);

		const classDoc = await getDoc(docRef)

		if (!classDoc.exists || classDoc.get("uid") !== user.uid) {
			// TODO: maybe do a class not found page
			goto("/classes");
		}

		positions = classDoc.get("positions") as Record<string, [number, number]>;
	});

	function takePhoto() {
		const context = canvasElement.getContext("2d");

		if (!context) {
			return;
		}

		context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

		return canvasElement.toDataURL("image/png");
	}

	async function sendPhoto(imageBase64: string) {
		// await fetch("/api/detect-slouch", {
		// 	method: "POST",
		// 	body: JSON.stringify({
		// 		image: imageBase64,
		// 		positions: positions,
		// 	})
		// });

		console.log(JSON.stringify({
				positions: positions,
			}) )
	}

	let intervalID: NodeJS.Timeout;

	onMount(() => {
		intervalID = setInterval(async () => {
			const dataURL = takePhoto();

			if (!dataURL) {
				return;
			}

			await sendPhoto(dataURL);
		}, 1000);
	})

	onDestroy(() => {
		clearInterval(intervalID);
	})
</script>

<Window>
	<!-- svelte-ignore a11y-media-has-caption -->
	<video bind:this={videoElement} class="w-full aspect-[4/3]"></video>
</Window>

<canvas class="hidden" bind:this={canvasElement}></canvas>
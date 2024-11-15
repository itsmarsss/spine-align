<script lang="ts">
  	import authStore from "$lib/stores/authStore";
  	import { createEventDispatcher, onDestroy, onMount } from "svelte";
  	import Window from "$lib/components/Window.svelte";
	import { doc, getDoc, setDoc } from "firebase/firestore";
	import { firestore } from "$lib/firebase";
	import { goto } from "$app/navigation";

	type SlouchCode = {
		slouching: true;
		confidence: number;
	} | {
		slouching: false;
	}

	export let classId: string | null = null;

	export let hideButton: boolean = false;
	let positions: Record<string, [number, number]>;

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;

	let yoloImage: string;
	let midasImage: string;
	let annotatedImage: string;

	const eventDispatcher = createEventDispatcher<{"video-play": {width: number, height: number}}>();

	authStore.subscribe(async (user) => {
		if (!user && classId) {
			return;
		}

		if (!("navigator" in globalThis)) {
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

		if (!user) {
			return
		}

		if (!classId) {
			return;
		}

		const docRef = doc(firestore, "classes", classId);

		const classDoc = await getDoc(docRef)

		if (!classDoc.exists() || classDoc.get("userID") !== user.uid) {
			// TODO: maybe do a class not found page
			goto("/classes");
		}

		positions = classDoc.get("positions") as Record<string, [number, number]>;

		intervalID = setInterval(async () => {
			const dataURL = takePhoto();

			if (!dataURL) {
				return;
			}

			await sendPhoto(dataURL);
		}, 1000);
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
		const response = await fetch("http://localhost:8080/process-image", {
			method: "POST",
			body: JSON.stringify({
				data_url: imageBase64,
				positions: positions,
			})
		});

		const reponseAsJson = await response.json();

		console.log(repsonseAsJson)

		const slouchCodes = reponseAsJson.slouchCodes as SlouchCode[];

		await Promise.all(slouchCodes.map(async (slouchCode, i) => {
			const qrCodeDocRef = doc(firestore, "classes", classId!, "qrcodes", i.toString());

			setDoc(qrCodeDocRef, slouchCode);
		}));
	}

	let intervalID: NodeJS.Timeout;

	onDestroy(() => {
		clearInterval(intervalID);
	})
</script>

<Window hideButton={hideButton} let:imageIndex>
	<!-- svelte-ignore a11y-media-has-caption -->
	<video bind:this={videoElement} class="w-full aspect-[4/3] {imageIndex === 0 ? '' : 'hidden'}"></video>

	{#if imageIndex === 1}
	<img src="data:image/jpeg;base64,{yoloImage}" class="w-full aspect-[4/3]"/>
	{:else if imageIndex === 2}
	<img src="data:image/jpeg;base64,{midasImage}" class="w-full aspect-[4/3]"/>
	{:else if imageIndex === 3}
	<img src="data:image/jpeg;base64,{annotatedImage}" class="w-full aspect-[4/3]"/>
	{/if}
	
</Window>

<canvas class="hidden" bind:this={canvasElement}></canvas>
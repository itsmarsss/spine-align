<script lang="ts">
  import { goto } from "$app/navigation";
	import VideoPlayer from "$lib/components/VideoPlayer.svelte";
	import { firestore } from "$lib/firebase";
	import type { Class } from "$lib/models/classes";
  	import authStore from "$lib/stores/authStore";
	import { addDoc, collection, doc, setDoc } from "firebase/firestore";

	let canvas: HTMLCanvasElement;
	let numQRCodes: number = 1;
	let name: string = "";

	let qrPoints: ([number, number] | null)[] = Array(numQRCodes);

	let currentQRIndex: number = -1;

	function onSelect(e: MouseEvent) {
		if (currentQRIndex == -1) {
			return;
		}

		qrPoints[currentQRIndex] = [e.offsetX, e.offsetY];

		const context = canvas.getContext("2d");
		context?.clearRect(0, 0, canvas.width, canvas.height);
		context!.fillStyle = "red";

		qrPoints.forEach(point => {
			if (!point) {
				return;
			}

			context?.fillRect(point[0] - 4, point[1] - 4, 8, 8);
		})

		currentQRIndex = -1;
	}

	function onSelectPoint(index: number) {
		return (e: MouseEvent) => {
			currentQRIndex = index;
		} 
	}

	function fitCanvas(e: CustomEvent<{ width: number, height: number}>) {
		canvas.width = e.detail.width;
		canvas.height = e.detail.height;
	}

	async function onSubmit() {
		const collectionRef = collection(firestore, "classes");
		
		const docRef = await addDoc(collectionRef, {
			name: name,
			userID: $authStore?.uid,
			positions: Object.fromEntries(qrPoints.map((point, i) => [i, point])),
			slouchedPositions: [],
		} as Class);
		
		for (let i = 0; i < numQRCodes; i++) {
			const qrCodeDocRef = doc(firestore, "classes", docRef.id, "qrcodes", i.toString());

			setDoc(qrCodeDocRef, {
				slouching: false,
			})
		}

		goto(`classes/${docRef.id}`);
	}
</script>

<main>
	<div class="dimensions-controls">
		<div>
			<label for="name">Class Name</label>
			<input type="text" name="name" id="name" bind:value={name}>
		</div>
		<div>
			<label for="num-qrs">Number of QR codes:</label>
			<input type="number" name="num-qrs" id="num-qrs" bind:value={numQRCodes}>
		</div>
		<div class="qrContainer">
			{#each Array(numQRCodes) as _, i}
				<div>
					<span>{i + 1}</span>
					<button on:click={onSelectPoint(i)}>{(qrPoints[i] === undefined || qrPoints[i] === null) ? "Select Point" : `(${qrPoints[i][0]}, ${qrPoints[i][1]})`}</button>
				</div>
			{/each}
		</div>

		<form action="" on:submit|preventDefault={onSubmit}>
			<button>Submit</button>
		</form>
	</div>
	<div class="video-player" on:click={onSelect}>
		<VideoPlayer on:video-play={fitCanvas} hideButton={true}/>
		<canvas bind:this={canvas}></canvas>
	</div>
</main>

<style lang="scss">
	main {
		display: flex;
		flex-direction: row;
		gap: 0.5rem;
	}

	canvas {
		position: absolute;
		inset: 0;

		z-index: 5;
	}

	.dimensions-controls {
		width: 60%;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;

		input {
			border: 1px solid black;
		}
	}

	.video-player {
		width: 40%;

		position: relative;
	}

	.box-button {
		width: 1.5rem;
		height: 1.5rem;
		background-color: blue;
	}
</style>


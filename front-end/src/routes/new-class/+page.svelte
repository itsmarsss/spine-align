<script lang="ts">
	import VideoPlayer from "$lib/components/VideoPlayer.svelte";
	import { firestore } from "$lib/firebase";
	import type { Class } from "$lib/models/classes";
  import authStore from "$lib/stores/authStore";
	import { addDoc, collection } from "firebase/firestore";

	let canvas: HTMLCanvasElement;
	let numEsps: number = 1;
	let name: string = "";

	let espIds: string[] = Array(numEsps)
	let espPoints: ([number, number] | null)[] = Array(numEsps);

	let currentEspIndex: number = -1;

	function onSelect(e: MouseEvent) {
		if (currentEspIndex == -1) {
			return;
		}

		espPoints[currentEspIndex] = [e.offsetX, e.offsetY];

		const context = canvas.getContext("2d");
		context?.clearRect(0, 0, canvas.width, canvas.height);
		context!.fillStyle = "red";

		espPoints.forEach(point => {
			if (!point) {
				return;
			}

			context?.fillRect(point[0] - 4, point[1] - 4, 8, 8);
		})

		currentEspIndex = -1;
	}

	function onSelectPoint(index: number) {
		return (e: MouseEvent) => {
			currentEspIndex = index;
		} 
	}

	function fitCanvas(e: CustomEvent<{ width: number, height: number}>) {
		canvas.width = e.detail.width;
		canvas.height = e.detail.height;
	}

	function onSubmit() {
		const collectionRef = collection(firestore, "classes");

		addDoc(collectionRef, {
			name: name,
			userID: $authStore?.uid,
			positions: Object.fromEntries(espIds.map((id, i) => [id, espPoints[i]])),
			slouchedPositions: [],
		} as Class);
	}
</script>

<main>
	<div class="dimensions-controls">
		<div>
			<label for="name">Class Name</label>
			<input type="text" name="name" id="name" bind:value={name}>
		</div>
		<div>
			<label for="num-esps">Number of ESPs:</label>
			<input type="number" name="num-esps" id="num-esps" bind:value={numEsps}>
		</div>
		<div class="espContainer">
			{#each Array(numEsps) as _, i}
				<div>
					<input type="text" bind:value={espIds[i]}>
					<button on:click={onSelectPoint(i)}>{(espPoints[i] === undefined || espPoints[i] === null) ? "Select Point" : `(${espPoints[i][0]}, ${espPoints[i][1]})`}</button>
				</div>
			{/each}
		</div>

		<form action="" on:submit={onSubmit}>
			<button>Submit</button>
		</form>
	</div>
	<div class="video-player" on:click={onSelect}>
		<VideoPlayer on:video-play={fitCanvas}/>
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


<script lang="ts">
  import { goto } from "$app/navigation";
	import VideoPlayer from "$lib/components/VideoPlayer.svelte";
	import { firestore } from "$lib/firebase";
	import type { Class } from "$lib/models/classes";
  	import authStore from "$lib/stores/authStore";
	import { addDoc, collection, doc, setDoc } from "firebase/firestore";

	let canvas: HTMLCanvasElement;
	let numQRCodes: number = 1;
	let className: string = "";
	let teacherName: string = "";

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
			if (currentQRIndex === index) currentQRIndex = -1; // cancel current selected point
			else currentQRIndex = index;
		} 
	}

	function fitCanvas(e: CustomEvent<{ width: number, height: number}>) {
		canvas.width = e.detail.width;
		canvas.height = e.detail.height;
	}

	async function onSubmit() {
		const collectionRef = collection(firestore, "classes");
		
		const docRef = await addDoc(collectionRef, {
			className: className,
			teacherName: teacherName,
			userID: $authStore?.uid,
			positions: Object.fromEntries(qrPoints.map((point, i) => [i.toString(), point])),
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

	let previousN = numQRCodes

	function validator(node: HTMLInputElement, value: number) {
	return {
		update(value: number) {
				numQRCodes = value === null || numQRCodes < +node.min ? previousN : parseInt(value as unknown as string)
		previousN = numQRCodes;
		}
	}
}
</script>

<main class="clamp-width my-8 mx-auto">
	<div class="controls">
		<div class="metadata flex flex-row justify-between gap-8">
			<div class="form-control metadata-control">
				<label for="class-name">Class Name</label>
				<input
				  required
				  type="text"
				  name="class-name"
				  id="class-name"
				  placeholder="Class Name"
				  bind:value={className}
				/>
			</div>

			<div class="form-control metadata-control">
				<label for="teacher-name">Teacher Name</label>
				<input
				  required
				  type="text"
				  name="teacher-name"
				  id="teacher-name"
				  placeholder="Teacher Name"
				  bind:value={teacherName}
				/>
			</div>
		</div>
		
		<div class="form-control">
			<label for="qr-num">Number of QR Codes</label>
			<input
			required
			min="1"
			use:validator={numQRCodes}
			type="number"
			name="qr-num"
			id="qr-num"
			placeholder="Number of QR Codes"
			bind:value={numQRCodes}
			/>
		</div>
		<span class="label">Assign QR Codes</span>
		<div class="qrContainer grid grid-cols-2 gap-y-4 gap-x-8 mb-2">
			{#each Array(numQRCodes) as _, i}
				<div class="flex flex-row gap-2 justify-between items-center">
					<span class="align-middle">QR ID {i + 1}</span>
					<button class="rounded-xl bg-accent hover:-translate-y-1 transition-transform px-2 py-1 drop-shadow-xl w-[7rem] transition-colors" class:text-black={i === currentQRIndex} class:text-white={i !== currentQRIndex} class:bg-light-gray={i === currentQRIndex} on:click={onSelectPoint(i)}>{(qrPoints[i] === undefined || qrPoints[i] === null) ? "Select Point" : `(${qrPoints[i][0]}, ${qrPoints[i][1]})`}</button>
				</div>
			{/each}
		</div>

		<form action="" on:submit|preventDefault={onSubmit}>
			<button class="rounded-xl bg-accent hover:-translate-y-1 transition-transform text-white px-2 py-1 drop-shadow-xl w-full">Submit</button>
		</form>
	</div>

	<div class="video-player {currentQRIndex === -1 ? '' : 'drop-shadow-[0_10px_8px_rgba(71,68,217,0.3)]'}" on:click={onSelect}>
		<VideoPlayer on:video-play={fitCanvas} hideButton={true}/>
		<canvas bind:this={canvas}></canvas>
	</div>
</main>

<style lang="scss">
	main {
		display: flex;
		flex-direction: row;
		gap: 6rem;
		justify-content: center;
	}

	canvas {
		position: absolute;
		inset: 0;

		z-index: 5;
	}

	.clamp-width {
		width: clamp(16rem, 80%, 84rem);
	}

	.controls {
		width: 40%;
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

	label, span.label {
    @apply font-bold block text-black w-full mb-[2px];
  }
  .form-control > input {
    @apply bg-light-accent rounded-md outline-none p-2 w-full placeholder-black;
  }

  .form-control > input:focus {
    @apply shadow-inner;
  }
</style>


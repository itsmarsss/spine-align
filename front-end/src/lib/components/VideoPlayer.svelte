<script lang="ts">
  	import authStore from "$lib/stores/authStore";

	let mediaStream: MediaStream;

	authStore.subscribe(async (user) => {
		if (!user) {
			return;
		}

		mediaStream = await navigator.mediaDevices.getUserMedia({
			video: true,
			audio: true,
		});

		
	})
</script>

<section>
	<video bind:this={}></video>
</section>
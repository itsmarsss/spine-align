<script lang="ts">
  	import authStore from "$lib/stores/authStore";

	authStore.subscribe(async (user) => {
		if (!user) {
			return;
		}
		
		const mediaStream = await navigator.mediaDevices.getUserMedia({
			video: true,
			audio: true,
		});
	})
</script>
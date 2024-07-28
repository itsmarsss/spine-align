<script lang="ts">
	import type PageServerData from "./$types"
  	import VideoPlayer from "$lib/components/VideoPlayer.svelte";

	export let data: PageServerData;
</script>

<main>
	<div class="size">
		<VideoPlayer classId={data.id}/>
	</div>
</main>

<style lang="scss">
	.size {
		margin: 1rem auto;
		width: max(30rem, calc(80% * 9 / 16 + 4rem));
	}
</style>
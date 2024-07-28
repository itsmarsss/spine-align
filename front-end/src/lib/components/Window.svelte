<script lang="ts">
  	import Icon from "@iconify/svelte";
  	import { createEventDispatcher } from "svelte";

	export let programText: string = "video.exe";
	export let imageIndex = 0;
	export let hideButton: boolean = false;

	const dispatch = createEventDispatcher<{ "slide-change": { index: number } }>();
</script>
<section class="rounded-xl overflow-hidden relative drop-shadow-md bg-light-gray">
	<div class="z-50 drop h-8 w-full absolute top-0 left-0 right-0 flex flex-row bg-white justify-between px-4 items-center">
		<p class="text-dark-gray">{programText}</p>
		<div class="flex flex-row gap-4">
			<Icon font-size="20px" class="text-dark-gray" icon="mdi:minimize" />
			<Icon font-size="20px" class="text-dark-gray" icon="mdi:window-restore" />
			<Icon font-size="20px" class="text-dark-gray" icon="mdi:close" />
		</div>
	</div>
	<slot/>
	<div class="z-50 drop h-8 w-full absolute bottom-0 left-0 right-0 flex flex-row bg-white justify-center px-4 items-center gap-4">
		{#if !hideButton}
			{#each Array(4) as _, i}
				<button on:click={() => {
					imageIndex = i;
					
					dispatch("slide-change", { index: imageIndex });
				}}>
					<Icon class="text-black hover:cursor-pointer" icon="material-symbols:circle{imageIndex === i ? '' : '-outline'}" />
				</button>
			{/each}
		{/if}

	</div>
</section>

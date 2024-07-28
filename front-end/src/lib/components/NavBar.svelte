<script lang="ts">
  import Icon from "@iconify/svelte";
  import { base } from "$app/paths";
</script>

<nav class="w-full flex flex-row h-20 justify-between px-8">
  <!-- Logo -->
  <h1 class="flex items-center text-2xl text-black">
    <Icon icon="ri:sparkling-fill" class="inline-block mr-1" />
    spine<span class="text-accent">align</span>
  </h1>
  <div class="flex justify-between gap-4 text-xl items-center">
    <a class="rounded-xl bg-accent text-white px-3 py-2 drop-shadow-xl" href="{base}/sign-up">
        Sign up
    </a>
    <a class="rounded-xl text-black" href="{base}/log-in">
        Log in
    </a>
  </div>
</nav>
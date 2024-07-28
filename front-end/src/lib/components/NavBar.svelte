<script lang="ts">
  import Icon from "@iconify/svelte";
</script>

<nav class="w-full bg-white flex flex-row justify-between">
  <!-- Logo -->
  <h1 class="flex items-center text-[36px]">
    <Icon icon="ri:sparkling-fill" class="inline-block mr-[36px]" />
    spine<span class="text-accent">align</span>
  </h1>
  <div class="flex justify-between bg-light-gray gap-4 text-[36px]">
    <a class="rounded-lg bg-accent text-white">
        Sign up
    </a>
    <a class="rounded-lg">
        Log in
    </a>
  </div>
</nav>
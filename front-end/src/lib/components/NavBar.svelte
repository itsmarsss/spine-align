<script lang="ts">
  import Icon from "@iconify/svelte";
  import { base } from "$app/paths";
  import authStore from "$lib/stores/authStore";
  import { firebaseAuth } from "$lib/firebase";
</script>

<nav class="w-full flex flex-row h-20 justify-between px-8 items-center">
  <!-- Logo -->
  <h1 class="text-2xl text-black">
    <a class="flex items-center w-full h-full" href="{base}/">
      <Icon icon="ri:sparkling-fill" class="inline-block mr-1" />
      spine<span class="text-accent">align</span>
    </a>
  </h1>
  {#if $authStore !== null}
    <p class="text-black">Welcome, {$authStore.displayName}!</p>
  {/if}
  <div class="flex justify-between gap-4 text-md">
    {#if $authStore === null}
      <a
        class="rounded-xl bg-accent hover:-translate-y-1 transition-transform text-white px-3 py-2 drop-shadow-xl"
        href="{base}/sign-up"
      >
        sign up
      </a>
      <a
        class="rounded-xl text-black hover:-translate-y-1 transition-transform"
        href="{base}/log-in"
      >
        log in
      </a>
    {:else}
      <a
        class="rounded-xl bg-accent hover:-translate-y-1 transition-transform text-white px-3 py-2 drop-shadow-xl"
        href="{base}/classes"
      >
        view classes
      </a>
      <button
        class="rounded-xl text-black hover:-translate-y-1 transition-transform"
        on:click={() => firebaseAuth.signOut()}
      >
        sign out
      </button>
    {/if}
  </div>
</nav>

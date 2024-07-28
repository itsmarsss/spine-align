<script lang="ts">
  import { base } from "$app/paths";
  import { firestore } from "$lib/firebase";
  import type { Class } from "$lib/models/classes";
  import authStore from "$lib/stores/authStore";
  import { collection, query, where, onSnapshot } from "firebase/firestore";

  let classes: Class[] = [];

  authStore.subscribe(async (user) => {
    if (!user) {
      return;
    }

    const collectionRef = collection(firestore, "classes");

    const q = query(collectionRef, where("userID", "==", user.uid));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      classes = snapshot.docs.map((doc) => {
        const data = doc.data();

        return {
          className: data.className,
          teacherName: data.teacherName,
          userID: data.userID,
          positions: data.positions,
          slouchedPositions: data.slouchedPositions,
          ID: doc.id
        };
      })
    });

    return unsubscribe;
  });

  $: JSON.stringify(classes);
</script>

<svelte:head>
  <title>Classes | Spine Align</title>
</svelte:head>
<main class="size flex flex-col items-center mx-auto">
  <div class="header flex justify-between w-full items-end mb-3">
    <h1 class="text-3xl">Your Classes</h1>
    <a href="/new-class">
      <button
        class="bg-accent rounded-lg py-2 px-3 text-white hover:-translate-y-1 transition-transform"
      >
        create class
      </button>
    </a>
  </div>
  <div class="classes flex flex-col w-full gap-3">
    {#each classes as classEntity}
      <a class="rounded-lg p-3 border-black border-[1px] hover:-translate-y-1 transition-transform" href="{base}/classes/{classEntity?.ID}">
        <h2>{classEntity.className}</h2>
        <h3>{classEntity.teacherName}</h3>
      </a>
    {/each}
  </div>
</main>

<style lang="scss">
  .size {
    width: min(60vw, 40rem);
  }
</style>

<script lang="ts">
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

		const unsubscribe = onSnapshot(q, snapshot => {
			classes = snapshot.docs.map(doc => doc.data() as Class);
			console.log(classes)
		});

		return unsubscribe;
	});

	$: JSON.stringify(classes)
</script>

<main>
	<div class="header">
		<h1>Your Classes</h1>
		<a href="/new-class">
			<button>
				Create Class
			</button>
		</a>
	</div>
	<div class="classes">
		{#each classes as classEntity}
			{JSON.stringify(classEntity)}
		{/each}
	</div>
</main>

<style lang="scss">
	.classes {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
	}

	.header {
		display: flex;
		flex-direction: row;
		justify-content: space-between;
	
		a {
			background-color: salmon;
		}
	}
</style>

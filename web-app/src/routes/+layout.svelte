<script>
	import '../app.css';
	import '../firebase';

	import { goto } from '$app/navigation';
	import { arrow, autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom';
	import {
		Modal,
		ProgressRadial,
		Toast,
		initializeStores,
		storePopup
	} from '@skeletonlabs/skeleton';
	import { onMount } from 'svelte';
	import { auth } from '../firebase';

	initializeStores();
	storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

	let loading = true;

	onMount(() => {
		auth.onAuthStateChanged((user) => {
			if (!user) {
				goto('/login');
			}
			loading = false;
		});
	});
</script>

<Modal />
<Toast />
{#if loading}
	<div class="flex h-screen items-center justify-center">
		<div class="card p-6">
			<ProgressRadial
				meter="stroke-primary-500"
				track="stroke-primary-500/30"
				strokeLinecap="round"
				width="w-16"
			/>
		</div>
	</div>
{:else}
	<slot />
{/if}

<script lang="ts">
	import { Avatar } from '@skeletonlabs/skeleton';
	import { auth } from '../firebase';
</script>

<div class="card z-50 space-y-4 p-6" data-popup="popupAvatarMenu">
	<Avatar src="https://avatars.githubusercontent.com/u/1004701?v=4" width="w-10" />
	<span class="text-sm font-semibold">{auth.currentUser?.email}</span>
	<button on:click={() => auth.signOut()} class="btn variant-soft-surface block w-full"
		>Sign Out</button
	>
</div>

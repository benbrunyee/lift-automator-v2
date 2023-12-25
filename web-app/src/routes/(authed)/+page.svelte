<script lang="ts">
	import Icon from '@iconify/svelte';
	import { Avatar, getToastStore } from '@skeletonlabs/skeleton';
	import { httpsCallable } from 'firebase/functions';
	import { onDestroy, onMount } from 'svelte';
	import { functions } from '../../firebase';
	import { facebookPostsSchema, type FacebookPost } from '../../lib/facebookPosts';
	import { toastError } from '../../lib/toastTrigger';

	const toastStore = getToastStore();

	let error: string | undefined = '';
	let hasErrored = false;
	let facebookPosts: FacebookPost[] = [
		{
			content: 'This is a test post',
			posted_at: new Date().getTime(),
			user: 'Test User',
			userLink: 'https://www.facebook.com/100000000000000',
			estimatedPricing: 10
		}
	];

	let interval: NodeJS.Timeout | undefined;

	onMount(() => {
		getPosts();
		interval = setInterval(getPosts, 3000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	async function getPosts() {
		error = undefined;

		const getPosts = httpsCallable(functions, 'getPosts');
		const result = await getPosts();

		try {
			facebookPosts = facebookPostsSchema.parse(result.data);
		} catch (e) {
			console.error(e);
			error = 'Failed to load posts';
			if (!hasErrored) {
				toastError(toastStore, error);
			}
			hasErrored = true;
		}
	}
</script>

<div class="table-container p-4">
	<div class="mb-4 text-left">
		{#if interval && !error}
			<span class="chip variant-glass-primary cursor-default">
				<Icon icon="ion:refresh" class="animate-spin " />
				<span>Refreshing every 3 seconds...</span>
			</span>
		{:else}
			<button
				class="chip variant-filled-error animate-pulse"
				on:click={() => {
					getPosts();
				}}
			>
				<Icon icon="ion:refresh" class="animate-pulse " />
				<span>Refresh</span>
			</button>{/if}
	</div>

	<table class="table-hover table">
		<thead>
			<tr>
				<th>Date/Time</th>
				<th>Post Text</th>
				<th>User</th>
				<th>Estimated Cost</th>
				<th>Message</th>
			</tr>
		</thead>

		<tbody>
			{#each facebookPosts as post}
				<tr>
					<td>{new Date(post.posted_at).toUTCString()}</td>
					<td class="flex">{post.content}</td>
					<td>
						<div class="flex items-center">
							<Avatar src="https://avatars.githubusercontent.com/u/1004701?v=4" width="w-6 mr-2" />
							{post.user}
						</div>
					</td>
					<td>
						<span class="chip variant-glass-secondary font-semibold">
							£{post.estimatedPricing}
						</span>
					</td>
					<td>
						<a href={post.userLink} target="_blank" class="chip variant-filled-primary">
							<Icon icon="ion:mail" />
							<span class="font-semibold">Message</span>
						</a>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<script lang="ts">
	import { goto } from '$app/navigation';
	import { toastError } from '$lib/toastTrigger';
	import Icon from '@iconify/svelte';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
	import { auth } from '../../../firebase';

	const toastStore = getToastStore();

	let email = '';
	let password = '';
	let submitting = false;
	let showPassword = false;

	$: if (showPassword) {
		setTimeout(() => {
			showPassword = false;
		}, 1000);
	}

	let type: 'sign-up' | 'log-in' = 'sign-up';

	async function submit() {
		if (submitting) return;
		submitting = true;

		if (type === 'log-in') {
			try {
				await signInWithEmailAndPassword(auth, email, password);
				goto('/');
			} catch (error) {
				console.error(error);
				toastError(toastStore, 'Invalid email or password');
			}
		} else if (type === 'sign-up') {
			try {
				await createUserWithEmailAndPassword(auth, email, password);
				goto('/');
			} catch (error) {
				console.error(error);
				toastError(toastStore, 'Failed to create account');
			}
		}

		submitting = false;
	}
</script>

<div class="flex h-full items-center justify-center">
	<div class="card space-y-4 p-6">
		<div class="flex justify-around space-x-6">
			<button
				class="btn {type === 'sign-up' && 'underline'}"
				on:click={() => {
					type = 'sign-up';
				}}>Sign Up</button
			>
			<button
				class="btn {type === 'log-in' && 'underline'}"
				on:click={() => {
					type = 'log-in';
				}}>Log In</button
			>
		</div>

		<form class="space-y-4">
			<div class="space-y-2">
				<input
					bind:value={email}
					type="email"
					autocomplete="email"
					placeholder="Email"
					class="input"
					disabled={submitting}
				/>
				<div class="input-group input-group-divider grid-cols-[1fr_auto]">
					{#if showPassword}
						<input
							bind:value={password}
							type="text"
							autocomplete={type === 'sign-up' ? 'new-password' : 'current-password'}
							placeholder="Password"
							class="input"
							disabled={submitting}
						/>
					{:else}
						<input
							bind:value={password}
							type="password"
							autocomplete={type === 'sign-up' ? 'new-password' : 'current-password'}
							placeholder="Password"
							class="input"
							disabled={submitting}
						/>
					{/if}
					<button
						on:click={() => {
							showPassword = !showPassword;
						}}
						tabindex="-1"
					>
						{#if showPassword}
							<Icon icon="ion:eye" />
						{:else}
							<Icon icon="ion:eye-off" />
						{/if}
					</button>
				</div>
			</div>

			<button
				type="submit"
				class="btn variant-filled-primary w-full text-white"
				on:click={() => {
					submit();
				}}
				disabled={submitting}
			>
				Submit
			</button>
		</form>
	</div>
</div>

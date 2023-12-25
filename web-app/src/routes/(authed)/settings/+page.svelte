<script lang="ts">
	import { getModalStore, getToastStore } from '@skeletonlabs/skeleton';
	import { httpsCallable } from 'firebase/functions';
	import { functions } from '../../../firebase';
	import {
		facebookAuthenticationResultSchema,
		type FacebookAuthenticationResult
	} from '../../../lib/facebookAuthenticationResult';
	import { toastError, toastSuccess } from '../../../lib/toastTrigger';

	const toastStore = getToastStore();
	const modalStore = getModalStore();

	let form = {
		email: '',
		password: '',
		shouldAutoreply: true
	};
	let show2FaModal = false;
	let checkingAuthentication = false;

	$: if (show2FaModal) {
		modalStore.trigger({
			title: '2FA Required',
			body: 'Two-factor authentication is required to authenticate to Facebook. Please enter the code from your authenticator app.',
			type: 'prompt',
			response: (code: string) => {
				submit2FaCode(code);
			}
		});
	}

	async function submit2FaCode(code: string) {
		let authenticationResult: FacebookAuthenticationResult;

		try {
			const response = await httpsCallable(
				functions,
				'submit2FaCode'
			)({
				code
			});

			authenticationResult = facebookAuthenticationResultSchema.parse(response.data);

			if (!authenticationResult.success) {
				throw new Error('Failed to authenticate with 2FA code');
			}
		} catch (e) {
			console.error(e);
			toastError(toastStore, 'Failed to authenticate with 2FA code');
			return;
		}
	}

	async function saveOptions() {}

	async function checkFacebookAuthentication() {
		if (checkingAuthentication) {
			return;
		}

		checkingAuthentication = true;

		let authenticationResult: FacebookAuthenticationResult;

		try {
			const response = await httpsCallable(
				functions,
				'checkFacebookAuthentication'
			)({
				email: form.email,
				password: form.password
			});

			authenticationResult = facebookAuthenticationResultSchema.parse(response.data);

			if (!authenticationResult.success) {
				if (authenticationResult.error === '2FA required') {
					show2FaModal = true;
					toastError(toastStore, '2FA is required to authenticate to Facebook');
					checkingAuthentication = false;
					return;
				} else {
					throw new Error('Failed to authenticate to Facebook');
				}
			}
		} catch (e) {
			console.error(e);
			toastError(toastStore, 'Failed to authenticate to Facebook');
			checkingAuthentication = false;
			return;
		}

		toastSuccess(toastStore, 'Successfully authenticated to Facebook');

		checkingAuthentication = false;
	}
</script>

<div class="card m-4 p-4">
	<form class="space-y-2" on:submit={() => saveOptions()}>
		<div class="flex items-center space-x-2">
			<input class="checkbox" type="checkbox" bind:checked={form.shouldAutoreply} />
			<label for="shouldAutoreply">Enable autoreply</label>
		</div>
		<span class="text-secondary-300"
			>Autoreply to posts that fit your criteria. <i>(Facebook Authentication is required)</i></span
		>

		{#if form.shouldAutoreply}
			<div class="space-y-2">
				<div class="space-y-2">
					<input
						class="input"
						bind:value={form.email}
						placeholder="Email"
						disabled={checkingAuthentication}
					/>
				</div>

				<div>
					<input
						class="input"
						bind:value={form.password}
						placeholder="Password"
						disabled={checkingAuthentication}
					/>
				</div>

				<button
					class="btn variant-soft-primary"
					on:click={() => checkFacebookAuthentication()}
					disabled={checkingAuthentication}>Check Authentication</button
				>
			</div>
		{/if}

		<button class="btn variant-filled-primary block" type="submit">Save</button>
	</form>
</div>

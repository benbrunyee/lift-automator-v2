<script lang="ts">
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';
	import {
		AppBar,
		AppRail,
		AppRailAnchor,
		AppShell,
		Avatar,
		popup,
		type PopupSettings
	} from '@skeletonlabs/skeleton';
	import AvatarPopup from '../../components/AvatarPopup.svelte';

	const popupAvatarMenu: PopupSettings = {
		event: 'click',
		target: 'popupAvatarMenu',
		placement: 'bottom'
	};
</script>

<AvatarPopup />
<AppShell>
	<svelte:fragment slot="header">
		<AppBar background="bg-surface-800" class>
			<svelte:fragment slot="lead"
				><h1 class="text-3xl font-bold text-white">Home</h1></svelte:fragment
			>
			<svelte:fragment slot="trail">
				<button use:popup={popupAvatarMenu}>
					<Avatar src="https://avatars.githubusercontent.com/u/1004701?v=4" width="w-10" />
				</button>
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>

	<svelte:fragment slot="sidebarLeft">
		<AppRail background="bg-surface-900">
			<svelte:fragment slot="lead">
				<AppRailAnchor href="/" selected={$page.url.pathname === '/'}>
					<div class="flex items-center justify-center">
						<Icon
							icon="ion:home"
							class="text-3xl {$page.url.pathname === '/' ? 'text-black' : 'text-white'}"
						/>
					</div>
				</AppRailAnchor>
			</svelte:fragment>

			<AppRailAnchor href="/settings" selected={$page.url.pathname === '/settings'}>
				<div class="flex items-center justify-center">
					<Icon
						icon="ion:settings"
						class="text-3xl {$page.url.pathname === '/settings' ? 'text-black' : 'text-white'}"
					/>
				</div>
			</AppRailAnchor>
		</AppRail>
	</svelte:fragment>

	<slot />
</AppShell>

import type { ToastStore } from '@skeletonlabs/skeleton';

export const toastError = (toastStore: ToastStore, message: string) => {
	toastStore.trigger({
		message,
		background: 'bg-error-500',
		autohide: true,
		classes: 'text-white'
	});
};

export const toastSuccess = (toastStore: ToastStore, message: string) => {
	toastStore.trigger({
		message,
		background: 'bg-success-500',
		autohide: true,
		classes: 'text-white'
	});
};

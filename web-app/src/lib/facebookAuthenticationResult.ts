import { z } from 'zod';

export const facebookAuthenticationErrorMessageSchema = z
	.literal('Authentication failed')
	.or(z.literal('Server error'))
	.or(z.literal('2FA required'));

export const facebookAuthenticationResultSchema = z
	.object({
		success: z.literal(true)
	})
	.or(
		z.object({
			success: z.literal(false),
			error: facebookAuthenticationErrorMessageSchema
		})
	);

export type FacebookAuthenticationResult = z.infer<typeof facebookAuthenticationResultSchema>;

import { z } from 'zod';

export const facebookPostSchema = z.object({
	content: z.string(),
	user: z.string(),
	userLink: z.string(),
	posted_at: z.number(),
	estimatedPricing: z.number()
});

export const facebookPostsSchema = z.array(facebookPostSchema);

export type FacebookPost = z.infer<typeof facebookPostSchema>;

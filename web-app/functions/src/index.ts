/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import * as logger from 'firebase-functions/logger';
import { CallableRequest, onCall } from 'firebase-functions/v2/https';

type FacebookAuthenticationResult =
	| {
			success: true;
	  }
	| {
			success: false;
			error: 'Authentication failed' | 'Server error' | '2FA required';
	  };

export const submit2FaCode = onCall(
	{},
	async (request: CallableRequest): Promise<FacebookAuthenticationResult> => {
		if (!request.auth) {
			throw new Error('Authentication Required');
		}

		logger.info('Submitting 2FA code');

		return {
			success: false,
			error: 'Authentication failed'
		};
	}
);

export const checkFacebookAuthentication = onCall(
	{},
	async (request: CallableRequest): Promise<FacebookAuthenticationResult> => {
		if (!request.auth) {
			throw new Error('Authentication Required');
		}

		logger.info('Checking Facebook authentication');

		return {
			success: false,
			error: '2FA required'
		};
	}
);

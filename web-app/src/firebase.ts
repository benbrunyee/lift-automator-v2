// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app';
import { connectAuthEmulator, getAuth } from 'firebase/auth';
import { connectFirestoreEmulator, getFirestore } from 'firebase/firestore';
import { connectFunctionsEmulator, getFunctions } from 'firebase/functions';
import { connectStorageEmulator, getStorage } from 'firebase/storage';

// Your web app's Firebase configuration
const firebaseConfig = {
	apiKey: 'AIzaSyDYNIIJyj4SuD7UKhAWGfxBsTHW32cuVtc',
	authDomain: 'lift-automator-v2.firebaseapp.com',
	projectId: 'lift-automator-v2',
	storageBucket: 'lift-automator-v2.appspot.com',
	messagingSenderId: '231914832872',
	appId: '1:231914832872:web:73d95e7ce5c3bf3c7e9a5d'
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const storage = getStorage(app);
export const functions = getFunctions(app);

if (process.env.NODE_ENV === 'development') {
	connectFirestoreEmulator(db, 'localhost', 8080);
	connectAuthEmulator(auth, 'http://localhost:9099');
	connectStorageEmulator(storage, 'localhost', 9199);
	connectFunctionsEmulator(functions, 'localhost', 5001);
}

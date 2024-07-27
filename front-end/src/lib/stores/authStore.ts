import { firebaseAuth } from "$lib/firebase";
import { createUserWithEmailAndPassword, sendPasswordResetEmail, signInWithEmailAndPassword, signOut, type User } from "firebase/auth";
import { writable } from "svelte/store";

const authStore = writable<User | null>(null);

export const signUp = async (email: string, password: string) => {
	return await createUserWithEmailAndPassword(firebaseAuth, email, password);
}

export const logIn = async (email: string, password: string) => {
	await signInWithEmailAndPassword(firebaseAuth, email, password)
}

export const logOut = async () => {
	await signOut(firebaseAuth);
}

export const resetPassword = async (email: string) => {
	await sendPasswordResetEmail(firebaseAuth, email);
}

export default authStore;
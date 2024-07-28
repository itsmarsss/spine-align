import { firebaseAuth } from "$lib/firebase";
import {
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
  type User,
} from "firebase/auth";
import { writable } from "svelte/store";

const authStore = writable<User | null>(null);

export const signUp = async (
  email: string,
  password: string,
  firstName: string,
  lastName: string
) => {
  const res = await createUserWithEmailAndPassword(
    firebaseAuth,
    email,
    password
  );
  await updateProfile(res.user, { displayName: firstName + " " + lastName });
  return res;
};

export const logIn = async (email: string, password: string) => {
  await signInWithEmailAndPassword(firebaseAuth, email, password);
};

export const logOut = async () => {
  await signOut(firebaseAuth);
};

export const resetPassword = async (email: string) => {
  await sendPasswordResetEmail(firebaseAuth, email);
};

export default authStore;

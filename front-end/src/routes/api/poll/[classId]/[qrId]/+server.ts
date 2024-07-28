import type { RequestHandler } from './$types';
import { firestore } from '$lib/firebase';
import { doc, getDoc } from 'firebase/firestore';

export const GET: RequestHandler = async ({ params }) => {
	const classId = params.classId;
	const qrId = params.qrId;

	const docRef = doc(firestore, "classes", classId, "qrcodes", qrId);

	const docData = await getDoc(docRef);

	if (!docData.exists()) {
		return new Response(JSON.stringify({ slouching: false }));
	}

	return new Response(JSON.stringify(docData.data()));
};
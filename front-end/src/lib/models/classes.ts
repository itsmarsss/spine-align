type Point = [number, number];

interface Class {
	name: string;
	userID: string;
	positions: Record<string, Point>;
	slouchedPositions: string[];
}

export type { Class, Point };
type Point = [number, number];

interface Class {
	className: string;
	teacherName: string;
	userID: string;
	positions: Record<string, Point>;
	slouchedPositions: string[];
	ID?: string;
}

export type { Class, Point };
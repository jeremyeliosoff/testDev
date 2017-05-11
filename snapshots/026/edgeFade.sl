surface edgeFade(
	float ndcFadeEdge = 0;
	float ndcFadeCent = 1;
	float ndcEdgy = .5;
	float ndcEdgyDist = 2.5;
) {

	point Pndc = transform("NDC", P);
	Pndc[2] = 0;
	float nearEdge = distance(Pndc, (point 0));
	nearEdge *= 210/297;
	float edgeFade = mix(ndcFadeCent, ndcFadeEdge, nearEdge/ndcEdgyDist);
	edgeFade = clamp(pow(edgeFade, 1/ndcEdgy), 0, 1);
	Ci = Cs * edgeFade;
}

surface edgeFade(
	float ndcFadeEdge = 0;
	float ndcFadeCent = 1;
	float ndcEdgy = .3;
	float ndcEdgyDist = 3;
	color fadeClr = color 0;
) {

	point Pndc = transform("NDC", P);
	Pndc = Pndc * 2 - vector 1;
	//Pndc = P;
	Pndc[2] = 0;
	float nearEdge = distance(Pndc, (point (0, -.17, 0)));
	nearEdge *= 210/297;
	float edgeFade = mix(ndcFadeCent, ndcFadeEdge, min(1, nearEdge/ndcEdgyDist));
	edgeFade = clamp(pow(edgeFade, 1/ndcEdgy), 0, 1);
	Ci = mix(fadeClr, Cs, edgeFade);
	Ci *= Os;
	//Ci[1] = edgeFade;
}

float nsin(float v) {
	float pi = 3.14159265359;
	return .5 + .5*sin(v*2*pi);
}

surface lDisk (
	float ndcFadeEdge = 0;
	float ndcFadeCent = 1;
	float ndcEdgy = .3;
	float ndcEdgyDist = 3;
		) {
	float edge = nsin(.25 + u);
	edge = mix(edge, .5, .5);
	//edge *= .5;
	//Ci = Cs*u;
	float side = filterstep(edge, v);
	float vv = nsin((u + 1/12)*3 + .5*side);
	vv = filterstep(.5, vv);

	float uu = mod(u*5, 1);
	point pp = (uu, v, 0);
	point cc = (.5, .5, 0);
	//float dd = distance(pp,cc)*.5/edge;
	float dd = distance(pp,cc);
	float dm = mod(dd*2, 1);
	float inDisk = filterstep(.5, dm);
	vv = inDisk;

	vv = mix(.2, 1.1, vv);

	point Pndc = transform("NDC", P);
	Pndc = Pndc * 2 - vector 1;
	//Pndc = P;
	Pndc[2] = 0;
	//float nearEdge = distance(Pndc, (point 0));
	float nearEdge = distance(Pndc, (point (0, -.17, 0)));
	float edgeFade = mix(ndcFadeCent, ndcFadeEdge, min(1, nearEdge/ndcEdgyDist));
	edgeFade = clamp(pow(edgeFade, 1/ndcEdgy), 0, 1);

	Ci =  vv*Cs*Os*edgeFade*1.5;
	Oi = Os;
}

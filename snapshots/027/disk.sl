surface disk(
	color cCent = 1;
	color cEdge = 0;
	float clrFadeCentral = 1;
	float fadeCentral = 1;
) {
	float k = pow(v, fadeCentral);
	Ci = mix(cEdge, cCent, pow(v, clrFadeCentral))*k;
}

surface disk(
	color cCent = 1;
	color cEdge = 0;
	color fadeClr = 0;
	float clrFadeCentral = 1;
	float fadeCentral = 1;
	float diskIntens = 1;
) {
	float k = pow(v, fadeCentral);
	Ci = mix(fadeClr, mix(cEdge, cCent, pow(v, clrFadeCentral)), k)*diskIntens;
	//Ci[0] = k;
}

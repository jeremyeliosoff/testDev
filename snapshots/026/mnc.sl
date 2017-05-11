surface mnc(
	color cCent = 1;
	color cEdge = 0;
	float diskCentral = 1;
) {
	Ci = mix(cEdge, cCent, pow(v, diskCentral));
}

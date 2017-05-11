imager mncImg (
	string texPath = "/home/jeremy/graphics/mnc/tex/graniteSq.tdl";
	string renPath = "/home/jeremy/graphics/mnc/img.tdl";
	float addBlur = .2;
	float texMult = .2;
){
	color Co = Ci;
	//point Pndc = transform("ndc", P);
	point Pndc = P/100;
	float k = 6;
	float rx = 210;
	float ry = 297;
	float ss = P[0]/(rx*k);
	float tt = P[1]/(ry*k);
	Ci[0] = mod(ss, 1);
	Ci[1] = mod(tt, 1);

	color tex = texture(texPath, ss*rx/ry, tt);

	color ren = texture(renPath, ss, tt);
	color renBlur = texture(renPath, ss, tt, "blur", .01);
	Ci = (ren + renBlur*addBlur)*mix(color 1, tex, texMult);
	//Ci = Co;
	Ci *= mix(color 1, Ci, .1);
}

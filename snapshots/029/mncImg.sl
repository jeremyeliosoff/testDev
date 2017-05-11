imager mncImg (
	string texPath = "/home/jeremy/graphics/mnc/tex/graniteSq.tdl";
	string renPath = "/home/jeremy/graphics/mnc/img.tdl";
	float addBlur = .05;
	float texMult = .2;
	float intens = 2;
	float rx = 210;
	float ry = 297;
	color tint = 1;
){
	color Co = Ci;
	//point Pndc = transform("ndc", P);
	point Pndc = P/100;
	//float k = 6;
	//float rx = 210;
	//float ry = 297;
	//float ss = P[0]/(rx*k);
	//float tt = P[1]/(ry*k);
	float ss = P[0]/(rx);
	float tt = P[1]/(ry);
	Ci[0] = mod(ss, 1);
	Ci[1] = mod(tt, 1);

	color tex = texture(texPath, ss*rx/ry, tt);

	color ren = texture(renPath, ss, tt, "width", 0);
	color renBlur = texture(renPath, ss, tt, "blur", .01);
	color lum = ctransform("hsl", renBlur);
	float texMixer = pow(min(lum[2]*1.8, 1), 2);
	color texMod = mix(tex, color .5, texMixer);
	Ci = (ren + renBlur*addBlur)*mix(color 1, texMod, texMult);
	//Ci = Co;
	Ci *= mix(color 1, Ci, .1)*intens;
}

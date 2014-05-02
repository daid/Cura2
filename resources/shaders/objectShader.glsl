//Simple per-pixel light shader.

varying vec3 normal;
varying vec3 position;

--VERTEX

void main()
{
	normal = normalize(gl_NormalMatrix * gl_Normal);
	position = vec3(gl_ModelViewMatrix * gl_Vertex);
	
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	gl_FrontColor = gl_Color;
	gl_BackColor = gl_Color;
}

--FRAGMENT

void main()
{
	vec3 lightDir = normalize(vec3(gl_LightSource[0].position) - position);
	float intensity = abs(dot(lightDir, normalize(normal))) * 0.8;
	
	gl_FragColor = vec4(gl_Color.rgb * intensity + vec3(gl_LightModel.ambient), gl_Color.a);
}

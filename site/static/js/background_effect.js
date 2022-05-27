function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min;
}
function lerp(start, end, t) {
    return start * (1 - t) + end * t;
}
colors = ['#21ffff', '#1ffee8', '#23f4ff']

pixels_on_screen = window.innerWidth*window.innerHeight;
particle_count = Math.round(pixels_on_screen/9835)

var width = window.innerWidth;
var height = window.innerHeight;
particles = new Array();
for(i = 0; i < particle_count; i++) {
	particle = new Map();
	setup_particle(particle, width, height);
	particles.push(particle);
}

function setup_particle(particle, width, height) {
	p_width = getRandomInt(5, 12);
	p_percent = (p_width-4)/8.0;
	particle.set('x', getRandomInt(0, width*0.9));
	particle.set('y', getRandomInt(height*0.3, height));
	particle.set('length', getRandomInt(50, 100));
	particle.set('width', p_width);
	particle.set('speed', getRandomInt(1, 5)*p_percent);
	particle.set('live_time', 0);
	particle.set('color', colors[getRandomInt(0, 3)]);
	particle.set('opacity', getRandomInt(5, 100)*p_percent/100.0);
}

function draw_effect(ctx) {
	var width = window.innerWidth;
	var height = window.innerHeight;

	particles.forEach((particle) => {
		speed = particle.get('speed');
		live_time = particle.get('live_time');
		live_time += 0.003*speed;
		if(live_time >= 1) {
			setup_particle(particle, width, height);
			return;
		}
		length = particle.get('length');
		
		line_width = particle.get('width');
		
		x = particle.get('x')+speed;
		y = particle.get('y')-speed;

		particle.set('x', x);
		particle.set('y', y);
		particle.set('live_time', live_time);

		if(live_time <= 0.1)
			line_width *= live_time*10;
		else if(live_time >= 0.9)
			line_width *= (1-live_time)*10;

		ctx.beginPath();
		ctx.moveTo(x-length/2, y+length/2);
		ctx.lineTo(x+length/2, y-length/2);
		ctx.lineWidth = line_width;
		ctx.strokeStyle = "#2C2F33";// particle.get('color');
		ctx.lineCap = 'round';
		ctx.globalAlpha = particle.get('opacity');
		ctx.stroke();
	});
	
// ctx.fillStyle = "#2C2F33";
// var width = window.innerWidth;
// var height = window.innerHeight;
// ctx.clearRect(0, 0, width, height);

// if(p_live.length < particle_count) {
// 	posX = getRandomInt(0, width);
//      		posY = getRandomInt(100, height);
//      		p_live.push(0)
//      		p_pos.push([posX, posY])
//      		//velX = getRandomInt(-2, 2);
//      		velX = 0;
//      		velY = getRandomInt(1, 3)*-1;
//      		p_velocity.push([velX, velY]);
//      		p_alpha.push(0);
//      		p_size.push(getRandomInt(5, 10))
// }

//       for(i = 0; i < p_live.length; i++){
//       	if(p_live[i] >= 200) {
//       		posX = getRandomInt(0, width);
//       		posY = getRandomInt(100, height);
//       		p_live[i] = 0;
//       		p_pos[i] = [posX, posY];
//       		//velX = getRandomInt(-2, 2);
//       		velX = 0;
//       		velY = getRandomInt(1, 3)*-1;
//       		p_velocity[i] = [velX, velY];
//       		p_alpha[i] = 0;
//       		p_size[i] = getRandomInt(5, 10)
//       		continue;
//       	}
//       	pos = p_pos[i];
//       	vel = p_velocity[i];
//       	//vel[0] = clamp(getRandomInt(-1, 2)+vel[0], -2, 2);
//       	pos[0] += vel[0];
//       	pos[1] += vel[1];
//       	p_live[i] += 1;
//       	if(p_live[i] < 150)
//       		p_alpha[i] = lerp(p_alpha[i], 0.5, 0.05);
//      		else
//      			p_alpha[i] = lerp(p_alpha[i], 0, 0.05);
//       	ctx.globalAlpha = p_alpha[i];
//       	ctx.fillRect(pos[0], pos[1], p_size[i], p_size[i]);
//   	}
}
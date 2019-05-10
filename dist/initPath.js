// ---------------------------------------------- special particle------------------------
var initPath = function(x, y){

	var buckets = colorStyles.map(function(){
		return [];
	});
	var pathParticleCount;
	path.push([x, y]);

	function creatPath(x, y){
		var path[];
		var pathParticle[x:,y:,xt:,yt:,age];
		pathParticle.x = x;
		pathParticle.y = y;
		for (var i = 0; i <= 10000; i++) {
			var v = field(x, y);
			var m = v[2];
			var xt = x + v[0];
			var yt = y + v[1];
			if (field(xt, yt)[2] !== null) {
				// Path from (x,y) to (xt,yt) is visible, so add this particle to the appropriate draw bucket.
				pathParticle.xt = xt;
				pathParticle.yt = yt;
				path.push(pathParticle);
				pathParticle.x = xt;
				pathParticle.y = yt;
			} else {
				return path[];
		}
		}
	}
	function evolve_path(){
		var v = field(x, y);
		var m = v[2];
		var xt = x + v[0];
		var yt = y + v[1];
		path.push([xt, yt]);
		console.log(path);
		if (field(xt, yt)[2] !== null) {
			// Path from (x,y) to (xt,yt) is visible, so add this particle to the appropriate draw bucket.
			pathParticle.xt = xt;
			pathParticle.yt = yt;
			buckets[colorStyles.indexFor(m)].push(pathParticle);
		} else {
			// pathParticle isn't visible, but it still moves through the field.
			pathParticle.x = xt;
			pathParticle.y = yt;
		}
	}
	
	function drawPath(){
		buckets.forEach(function(bucket, i){
			if ((bucket.length > 0)) {
				g.beginPath();
				g.strokeStyle = colorStyles[i];
				bucket.forEach(function(pathParticle){
					g.moveTo(pathParticle.x, pathParticle.y);
					g.lineTo(pathParticle.xt, pathParticle.yt);
					pathParticle.x = pathParticle.xt;
					pathParticle.y = pathParticle.yt;
				})
				g.stroke();
			}
		})
	}

	var then = Date.now();
	(function frame() {
		animationLoop = requestAnimationFrame(frame);
		var now = Date.now();
		var delta = now - then;
		if (delta > FRAME_TIME) {
			then = now - delta % FRAME_TIME;
			evolve();
			draw();
		}
	})();
}
// ---------------------------------------------- -----------------------------------------

do{
	var x = pathParticle.x;
	var y = pathParticle.y;
	var v = field(x, y);
	// console.log(pathParticle.x + ',' +v[0])
	var m = v[2];
	var xt = x + v[0];
	var yt = y + v[1];
	pathParticle.xt = xt;
	pathParticle.yt = yt;
	// console.log(pathParticle);
	// path.push(pathParticle);//there are some mistakes
	path[pathCount] = pathParticle;
	console.log(path[pathCount]);
	pathParticle.x = xt;
	pathParticle.y = yt;
	pathCount +=1;
}while(m>=0.9)



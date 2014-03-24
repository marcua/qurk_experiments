
function ev_submit(tid, aid,wid,hid) {
	var svg = container.html();
	var nsec = $("#time").text();
	$("#btnbar").fadeOut(function(){$("#wait").show();});
	canvg(document.getElementById('canv'), svg );
	var pngdata = $("#canv")[0].toDataURL();
	$.post("/submit/", 
			{"tid" : tid,
			'png' : pngdata,
			"nsec" : nsec, 
			"nclear" : pencil.nclear, 
			"nundo" : pencil.nundo}, 
			function(data) {
				if (data.status == "True") {
					$("#drawspace").slideUp(function(){$("#drawspacedone").slideDown();});
				} else {
					$("#btnbar").show();
					$("#wait").hide();
					$("#error").html(data.error)
				}
	}, "json").error(function(){
		$("#btnbar").show();
		$("#wait").hide();
	});
	
}
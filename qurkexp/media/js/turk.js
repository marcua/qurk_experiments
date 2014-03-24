
function ev_submit(tid, aid,wid,hid) {
	var svg = container.html();
	var nsec = $("#time").text();
	$("#btnbar").fadeOut(function(){$("#wait").show();});
	canvg(document.getElementById('canv'), svg );
	var pngdata = $("#canv")[0].toDataURL();	
	
	// $("#f_png").val(encodeURIComponent(pngdata));
	// $("#f_nsec").val(nsec);
	// $("#f_nclear").val(pencil.nclear);
	// $("#f_nundo").val(pencil.nundo);

	
	$.post("/submit/", 
			{"aid" : aid, 
			"tid" : tid,
			"wid" : wid,
			'hid' : hid,
			"png" : pngdata,
			"nsec" : nsec, 
			"nclear" : pencil.nclear, 
			"nundo" : pencil.nundo}, 
			function(data) {
				if (data.status == "True") {
					$("#wait").slideUp();
					$("#form_turk").submit()									
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

function ev_submit(aid,wid,hid,tid,iid,val) {
	$.post("/submitverify/", 
			{"aid" : aid, 
			"wid" : wid,
			'hid' : hid,
			'tid' : tid,
			'iid' : iid,
			'val' : val,
			},
			function(data) {
				if (data.status == "True") {
					$("#btnbar").slideUp();
					$("#f_result").val(val);
					$("#form_turk").submit()									
				} else {
						$("#btnbar").show();
						$("#error").html(data.error)					
				}
	}, "json").error(function(){
		$("#btnbar").show();
	});
	
}


$(document).ready(function() {

	$("#showcentertile").click(function() {
		$('#coverlay').fadeIn(function(){setTimeout(function(){$('#coverlay').fadeOut()}, 700)})
	});
	
})
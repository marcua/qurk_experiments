var maxwidth = 100.0;
var maxheight = 100.0;

function resize(e) {
	var w = e.width();
	var h = e.height();
	var scale = Math.max(w / maxwidth, h / maxheight, 1.0);
	e.css({'width' : w / scale, 'height' : h / scale});
    //console.log('resizing?');
//	e.width(e.width() / scale);
//	e.height(e.height() / scale);
}

function resizepreview(e) {
	var w = e.width();
	var h = e.height();
	var scale = Math.max(w / 300, 1.0);
	//console.log(w + "," + h + "\t" + (w / scale) + "," + (h/scale));
	e.css({'width' : w / scale, 'height' : h / scale});	
}

//Get the absolute position of a DOM object on a page
function findPos(obj) {
	var pos = $(obj).position();
//	return {x: pos.left, y: pos.top};
    var curLeft = curTop = 0;
    if (obj.offsetParent) {
        do {
                curLeft += obj.offsetLeft;
                curTop += obj.offsetTop;
        } while (obj = obj.offsetParent);
    }
    return {x:curLeft, y:curTop};
}


function addpair(src, dst) {
	var fieldid = "radio_" + src.attr("pk") + "_" + dst.attr("pk");
	var lineid = "line_" + src.attr("pk") + "_" + dst.attr("pk");
	
	// validate it hasn't been added already
	if ($("#"+fieldid).val() == 'true') return;
	
	// make sure check box is not set
	$("#cb_nopairs").attr('checked', false);
	
	createline(src, dst);	
	
    if ($("#matchnote").size() == 0) {
        $("#matchcontainer").append($("<div id='matchnote'>To remove a pair added in error, click on the pair in the list below.</div>"));
    }
	var el = $("<div class='match'></div>");
	el.attr("lpk", src.attr("pk")).attr("rpk", dst.attr("pk"));
	$("#matchcontainer").append(el);	
	var limg = $("<img src='"+src.attr('src')+"'> </img>");
	var rimg = $("<img src='"+dst.attr('src')+"'> </img>");	
	limg.css({'width' : src.width(), 'height' : src.height()});
	rimg.css({'width' : dst.width(), 'height' : dst.height()});
	el.append(limg).append(rimg);	
	
	$("#" + fieldid).val('true');
	var tmp = el.clone();	
	el.hover(function(){
		pos = $("#previewtd").offset();
		tmp.removeClass("match").addClass("bigmatch");
		tmp.css({
		'position' : "relative", 
		"left" : 0,//pos.left,
		'top' : 0});//Math.max(pos.top, 100+$("body").scrollTop())});
		tmp.find("img").css({'width':'', 'height':''});
		$("#previewtd").append(tmp);
	}, function() {
		$("#previewtd").empty();
	})
	
	el.click(function() {
		$("#" + fieldid).val('false');	
		$("#" + lineid).remove();
		el.remove();
		$("#previewtd").empty();		
	})
}

function createline(src, dst) {
	var srcpos = findPos(src[0]);
	var dstpos = findPos(dst[0]);
	var newid = "line_" + src.attr("pk") + "_" + dst.attr("pk");
	dstpos = {x:dst.offset().left, y:dst.offset().top};
	//console.log(dst[0].id);
	
	var start = {x : srcpos.x + src.width(), y : srcpos.y + (src.height()/2.0)};
	var end = {x : dstpos.x, y : dstpos.y + (dst.height() / 2.0)};
	if (Math.abs(end.y - start.y) < 5) {
		end.y = start.y + (((end.y - start.y > 0)? 1:-1) * 5);
	}
	//console.log('CANVAS:' + start.x + ',' + start.y + '  to  ' + end.x + ',' + end.y);
	var mog = $("body");
	var canvasel = document.createElement('canvas');
	document.getElementsByTagName('body')[0].appendChild(canvasel)
	if (typeof(G_vmlCanvasManager) != 'undefined')
      G_vmlCanvasManager.initElement(canvasel);
	var canvas = $(canvasel);
	canvas.attr('id', newid);
	canvas.css({
		"position":"absolute",
		"left":Math.min(start.x, end.x),
		"top":Math.min(start.y, end.y)
	});

	//mog.append(canvas);	

	var ctx = canvasel.getContext('2d');
	ctx.canvas.width = Math.abs(end.x - start.x);
	ctx.canvas.height = Math.abs(end.y - start.y);
	ctx.lineWidth = 1.5;
	ctx.beginPath();
	var sx = 0;
	var sy = (end.y < start.y)? canvas.height() : 0;
	var ex = canvas.width();
	var ey = (end.y < start.y)? 0 : canvas.height();			
	ctx.moveTo(sx,sy);
	ctx.lineTo(ex,ey);
	//console.log('line:' + sx + "," + sy + "  to  " + ex + "," + ey);
	ctx.stroke();	
}

function previewable(e) {
	e = $(e);
	var img = $("<img src='"+e.attr('src')+"'> </img>");
	img.width(300);	
	
	e.hover(function(){
		pos = $("#previewtd").offset();
		img.css({
		'position' : "absolute", 
		"left" : pos.left,
		'top' : Math.max(pos.top, 100+$("body").scrollTop())});
		$("body").append(img);
	}, function() {
		img.remove();
	})
}



var lselected = null;
var rselected = null;

function clickable(e) {
	e = $(e);
    if (e.attr('class') == "leftimg") {
        lclickable(e);
    } else if (e.attr('class') == "rightimg") {
        rclickable(e);
    }
}

function lclickable(e) {
	e.click(function() {
		if (rselected != null) {
			addpair(e, rselected);
			$(".leftimg, .rightimg").removeClass('selected');
			lselected = null;
			rselected = null;
		} else {
			$(".leftimg").removeClass('selected');
			e.addClass('selected');
			lselected = e;
		}
	});

}

function rclickable(e) {
	e.click(function() {
		if (lselected != null) {
			//console.log(e[0]);
			addpair(lselected, e);
			$(".leftimg, .rightimg").removeClass('selected');
			lselected = null;
			rselected = null;
		} else {
			$(".rightimg").removeClass('selected');
			e.addClass('selected');
			rselected = e;
		}
	});
}

function unescapeURL(s) {
        return decodeURIComponent(s.replace(/\+/g, "%20"))
}

function getURLParams() {
    var params = {};
    var m = window.location.href.match(/[\\?&]([^=]+)=([^&#]*)/g);
    if (m) {
        for (var i = 0; i < m.length; i++) {
            var a = m[i].match(/.([^=]+)=(.*)/);
            params[unescapeURL(a[1])] = unescapeURL(a[2]);
        }
    }
    return params;
}


function submit() {
    $(".errmsg").text("");
    errors = false;
    if (($(".match").size() == 0) && !$("#cb_nopairs").attr("checked")) {
        $(".errmsg").text("You have not selected any pairs.  If you have determined that there are no pairs, please check the 'I did not find any pairs' box");
        errors = true;
    }
    if (!errors) {
        $("#form_turk").submit();
    }
}

function cb_change(checked) {
	if (checked) {
		// super hack attack!
		$("canvas, .match").remove();
		$(".hiddenfield").val("false")
	}
}


$(document).ready(function() {
    //console.log('at ready');	
	$(".leftimg, .rightimg").each(function(i,e) {
//		$(e).load(function() {previewable(e); resize($(e));});
		previewable(e);
        //resize($(e));
	});
	
    var params = getURLParams();
	$(".leftimg, .rightimg").each(function(i,e) {
	    clickable(e);
	});
	$('#assignmentId').attr('value', params.assignmentId);
	$("#submit_btn").click(function() {
	    submit();
	});
	$("#cb_nopairs").click(function() {
	cb_change($(this).attr("checked"));
	});
    

});

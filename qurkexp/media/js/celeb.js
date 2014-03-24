function unescapeURL(s) {
        return decodeURIComponent(s.replace(/\+/g, "%20"))
}

function getURLParams() {
    var params = {}
    var m = window.location.href.match(/[\\?&]([^=]+)=([^&#]*)/g)
    if (m) {
        for (var i = 0; i < m.length; i++) {
            var a = m[i].match(/.([^=]+)=(.*)/)
            params[unescapeURL(a[1])] = unescapeURL(a[2])
        }
    }
    return params
}


function submit(yesno) {
    $("#same").val(yesno);
    $("#form_turk").submit();	
}


$(document).ready(function() {
    var params = getURLParams();
    if (params.assignmentId && (params.assignmentId != "ASSIGNMENT_ID_NOT_AVAILABLE")) {      
        $('#assignmentId').attr('value', params.assignmentId);
        $("#btn_yes").click(function() {
            submit("yes");
        });
        $("#btn_no").click(function() {
            submit("no");
        });
    } else {
        $("#btn_yes").attr("disabled", "true");
        $("#btn_no").attr("disabled", "true");
    }
})

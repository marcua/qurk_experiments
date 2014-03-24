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


function submit() {
    $(".errmsg").text("");
    errors = false;
    $(".featureDropdown").each(function(index) {
       if ($(this).attr("value") == "default") {
           $(".errmsg", $(this).closest(".feature")).text("Please select a value");
           errors = true;
       }
    });
    if (!errors) {
        $("#form_turk").submit();
    }
}


$(document).ready(function() {
    var params = getURLParams();
    if (params.assignmentId && (params.assignmentId != "ASSIGNMENT_ID_NOT_AVAILABLE")) {      
        $('#assignmentId').attr('value', params.assignmentId);
        $("#submit_btn").click(function() {
            submit();
        });
    } else {
        $("#submit_btn").attr("disabled", "true");
        $(".featureDropdown").attr("disabled", "true");
    }
})

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

function timeNow() {
    return (new Date().getTime()) / 1000;
}

function setMetricFields() {
    var prevTime = $("#seconds_spent").data("startTime");
    var diff = Math.round((timeNow() - prevTime) * 100) / 100;
    $("#seconds_spent").attr("value", diff);

    $("#screen_height").attr("value", $(window).height());
    $("#screen_width").attr("value", $(window).width());
}

function submit() {
    $(".errmsg").text("");

    errors = submitTest();

    if (!errors) {
        setMetricFields();
        setFormFields();
        $("#form_turk").submit();
    }
}

$(document).ready(function() {
    var params = getURLParams();
    if (params.assignmentId && (params.assignmentId != "ASSIGNMENT_ID_NOT_AVAILABLE")) {      
        $("#assignmentId").attr('value', params.assignmentId);
        $("#submit_btn").click(function() {
            submit();
            return false;
        });
        $("#seconds_spent").data('startTime', timeNow());
        validSetup();
    } else {
        $("#submit_btn").attr("disabled", "true");
        invalidSetup();
    }
})

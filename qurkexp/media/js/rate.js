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
    $("#globalerror").text("");
    var errors = false;
    $(".val_container").each(function(index) {
        var cont = $(this);
        var radioval = $("input:radio:checked", cont).val();
        if (radioval === undefined) {
            $(".errmsg", cont).text("Please select a value");
            $("#globalerror").text("Please complete the tasks above");
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
        $(".val_rate").attr("disabled", "true");
    }
    $(".square").each(function(i) {
        var t = $(this);
        t.css("width", t.attr("size"));
        t.css("height", t.attr("size"));
    });
})

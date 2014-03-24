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

function assignEquality(items, group) {
    for (var i = 0; i < items.length; i++) {
        for (var j = i+1; j < items.length; j++) {
            var left = Math.min(items[i], items[j]);
            var right = Math.max(items[i], items[j]);
            $("#order_"+group+"_"+left+"_"+right).attr("value", "eq");
        }
    }
}

function assignInequality(orders, smalleri, smallerj, group) {
    for (var i = smalleri+1; i < orders.length; i++) {
        if (!(typeof orders[i] === "undefined")) {
            for (var j = 0; j < orders[i].length; j++) {
                var left = Math.min(orders[smalleri][smallerj], orders[i][j]);
                var right = Math.max(orders[smalleri][smallerj], orders[i][j]);
                var ltgt = (left == orders[smalleri][smallerj]) ? "lt" : "gt";
                $("#order_"+group+"_"+left+"_"+right).attr("value", ltgt);
            }
        }
    }
}

function assignComparisons(group, orders) {
    for (var i = 0; i < orders.length; i++) {
        if (!(typeof orders[i] === "undefined")) {
            assignEquality(orders[i], group);
            for (var j = 0; j < orders[i].length; j++) {
                assignInequality(orders, i, j, group);
            }
        }
    }

}

function setFormFields() {
    $(".group_container").each(function(index) {
        var orders = [];
        var group = -1;
        $(".val_order", $(this)).each(function(index) {
            var input = $(this);
            var parts = input.attr('id').split("_");
            var item = parts[2];
            group = parts[1];
            var order = input.val();
            if (!(order in orders)) {
                orders[order] = []; 
            }
            orders[order].push(item);
        });
        assignComparisons(group, orders);
    });
}

function submit() {
    $(".errmsg").text("");
    errors = false;
    $(".val_container").each(function(index) {
       var order = parseInt($(".val_order", $(this)).val());
       if (isNaN(order) || (order < 1) || (order > MAX_LENGTH)) {
           $(".errmsg", $(this)).text("Enter an order value between 1 and " + MAX_LENGTH);
           $("#globalerror").text("Please complete the tasks above");
           errors = true;
       }
    });

    if (!errors) {
        setFormFields();
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
        $(".val_order").attr("disabled", "true");
    }
    $(".square").each(function(i) {
        var t = $(this);
        t.css("width", t.attr("size"));
        t.css("height", t.attr("size"));
    });
})

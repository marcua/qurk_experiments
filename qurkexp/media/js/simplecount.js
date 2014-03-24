function setFormFields() {
}

function submitTest() {
    var errors = false;
    $(".count_container").each(function(index) {
        var count = parseInt($(".count", $(this)).val())
        var cStrIsDigits = $(".count", $(this)).val().match("^\\d+$");
        if (isNaN(count) || !cStrIsDigits || (count < 0) || (count > NUM_ITEMS)) {
           $(".errmsg", $(this)).text("Enter a value between 0 and " + NUM_ITEMS);
           $("#globalerror").text("Please complete the tasks above");
           errors = true;
       }
    });

    return errors;
}

function validSetup() {
}

function invalidSetup() {
    $(".count").attr("disabled", "true");
}
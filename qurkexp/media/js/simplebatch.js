function setFormFields() {
}

function submitTest() {
    var errors = false;
    $(".answer_container").each(function(index) {
        var choice = $(".value_radio:checked", $(this)).val();
        if (typeof(choice) === "undefined") {
           $(".errmsg", $(this)).text("Select a value");
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
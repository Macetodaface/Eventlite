/**
 * Created by Chris on 11/30/2016.
 */

//From django docs
function setCsrf(){
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
    });
}

function setupInterestBtn() {
    var btn = $('#interest');
    btn.click(function() {
        $.post('/show-interest', {
            id: id
        }).success()
    })
}

$(document).ready(function () {
    setCsrf();
    setupInterestBtn
});
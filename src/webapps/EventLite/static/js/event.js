/**
 * Created by Chris on 11/30/2016.
 */

var EVENT_ID;

//From Django docs
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//From django docs
function setCsrf(){
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
    });
}

function setId() {
    EVENT_ID = ($('#event-id')[0].innerHTML);
}

function setInterestedText() {
    var btn = $('#interest');
    $.get('/get-interest/' + EVENT_ID)
        .success(function(data){
            var interested = data;
            btn.empty();
            if (interested == 'True'){
                newText = 'Remove Interest';
            }
            else {
                newText = 'Show Interest';
            }
            btn.append(newText);
            updateInterestedCount(interested);
        });
}

function updateInterestedCount(interested) {
    var count = $('#interested-cnt');
    var text = $('interested-text');
}

function setupInterestBtn() {
    setInterestedText();
    var btn = $('#interest');
    btn.click(function() {
        $.post('/show-interest/' + EVENT_ID)
            .success(function (data) {
                setInterestedText();
        })
    })
}

$(document).ready(function () {
    setCsrf();
    setId();
    setupInterestBtn();
});
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

function setInterestedText(first) {
    var btn = $('#interest');
    $.get('/get-interest/' + EVENT_ID)
        .success(function(data){
            var interested = (data=='True');
            btn.empty();
            if (interested){
                newText = 'Remove Interest';
            }
            else {
                newText = 'Show Interest';
            }
            btn.append(newText);
            if(!first) {
                updateInterestedCount(interested);
            }
        });
}

function updateInterestedCount(interested) {
    countel = $('#interested-cnt');
    var count = parseInt(countel.html());
    countel.empty();
    if(interested){
        count += 1;
    }
    else {
        count -= 1;
    }
    countel.html(count);
    var textel = $('#interested-text');
    textel.empty();
    console.log(count);
    if(count == 1) {
        var text = 'person is interested in this event.';
    }
    else {
        var text = 'people are interested in this event.';
    }
    textel.html(text);
}

function setupInterestBtn() {
    setInterestedText(true);
    var btn = $('#interest');
    btn.click(function() {
        $.post('/show-interest/' + EVENT_ID)
            .success(function (data) {
                setInterestedText(false);
        })
    })
}

$(document).ready(function () {
    setCsrf();
    setId();
    setupInterestBtn();
});
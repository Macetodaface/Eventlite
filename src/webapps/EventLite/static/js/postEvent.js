/**
 * Created by Chris Grabowski on 11/14/2016.
 */


function addTicketTypeForm() {
    console.log("YAY");
    $.get("/ticket-type-html")
        .done(function(data) {
            var ticketTypes = $("#ticket-types");
            ticketTypes.append(data);
        });
}

function saveCurrentTicket() {
    name = $('#id_name');
    console.log(name.length);
    console.log(name);
    price = $('#id_price');
}

function newTicket() {
    saveCurrentTicket();
    addTicketTypeForm();
}

function addClickHandlers(){
    $("#add-ticket").click(newTicket);
    console.log("Added click handler!")
}

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

$(document).ready(function () {
    setCsrf();
    addClickHandlers();
    addTicketTypeForm();
});
/**
 * Created by Chris Grabowski on 11/14/2016.
 */

var TICKET_ID = 0;
var TICKET_IDS = [];

function submit() {
    var ticketsData = [];
    for(var i=0; i < TICKET_IDS; i++){
        var id = TICKET_IDS[i];
        ticketsData.push(getTicketData(id));
    }

    var eventData = {
        name: $('id_name').val(),
        description: $('description').val(),
        location: $('location').val(),
        time: $('time').val(),
        media: $('media').val(),
        email: $('email').val()
    };

    $.post('/post-event', {
        tickets_data: ticketsData,
        event_data: eventData
    });
}

function addTicketTypeForm() {
    $.get("/ticket-type-html/" + TICKET_ID)
    .done(function(data) {
        var ticketTypes = $("#ticket-types");
        ticketTypes.append(data);
        (function () {
            var id = TICKET_ID;
            $('#delete-btn-' + id).click(function () {
                deleteTicket(id)
            });
        })();
        TICKET_IDS.push(TICKET_ID);
        TICKET_ID ++;
    });
}


function deleteTicket(id) {
    $('#ticket-type-' + id).remove();
    for(var i=0; i < TICKET_IDS.length; i++){
        if (id === TICKET_IDS[i]){
            TICKET_IDS.splice(i, 1);
        }
    }
}

function getTicketData(id) {
    var data = {};
    var name = $('#ticket-name-' + id);
    var price = $('#ticket-price-' + id);
    var details = $('#ticket-details-' + id);
    var numOfTickets = $('#ticket-numOfTickets-' + id);

    data['name'] = name.val();
    data['price'] = price.val();
    data['details'] = details.val();
    data['numOfTickets'] = numOfTickets.val();

    return data
}

function addClickHandlers(){
    $("#add-ticket").click(addTicketTypeForm);
    $("#post-event").click(submit);
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
});
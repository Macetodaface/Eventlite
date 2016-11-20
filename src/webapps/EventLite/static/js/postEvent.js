/**
 * Created by Chris Grabowski on 11/14/2016.
 */

var TICKET_ID = 0;
var TICKET_IDS = [];
var lat='default';
var long='default';
var globalMap = ''
var geoCoder = ''

function submit() {
    var ticketsData = [];
    for(var i=0; i < TICKET_IDS; i++){
        var id = TICKET_IDS[i];
        ticketsData.push(getTicketData(id));
    }

    // just in case
    // if the user attempts to resubmit the form without
    // pressing enter in the location
    geocodeAddress(geoCoder, globalMap);

    $.post('/post-event', {
        name: $('id_name').val(),
        description: $('id_description').val(),
        location: $('id_location').val(),
        time: $('id_time').val(),
        media: $('id_media').val(),
        email: $('id_email').val(),
        tickets_data: ticketsData,
        latitude: lat,
        longitude:long
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

// Map Stuff

window.initMap = function () {
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,
    center: {lat: -34.397, lng: 150.644}
  });
  var geocoder = new google.maps.Geocoder();
  geoCoder = geocoder;
  globalMap = map;

  document.getElementById('id_location').addEventListener('keypress', function(e)
  {
      if(e.keyCode == 13)
      {
          geocodeAddress(geocoder, map);
      }
});

}

function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('id_location').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      resultsMap.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
        lat=results[0].geometry.location.latitude
        long=results[0].geometry.location.longitude
      });
    } else {
      alert('Enter a valid location! ');
    }
  });
}


$(document).ready(function () {
    setCsrf();
    addClickHandlers();

});

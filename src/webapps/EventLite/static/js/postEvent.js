/**
 * Created by Chris Grabowski on 11/14/2016.
 */

var TICKET_ID = 0;
var TICKET_IDS = [];
var lat='default';
var long='default';
var globalMap = ''
var geoCoder = ''

function submit()
{
    var ticketsData = [];
    for(var i=0; i < TICKET_IDS.length; i++){
        var id = TICKET_IDS[i];
        ticketsData.push(getTicketData(id));
    }

    console.log(ticketsData)

    // just in case
    // if the user attempts to resubmit the form without
    // pressing enter in the location
    geocodeAddress(geoCoder, globalMap);

    //"22 November 2016 - 13:25"
    var splits = $('#id_time').val().split(" ");
    var date = splits[0];
    var month = splits[1];
    var year = splits[2];
    var time = splits[4];

    //change month to number
    var dict = {
        'January':1,
        'February':2,
        'March':3,
        'April':4,
        'May':5,
        'June':6,
        'July':7,
        'August':8,
        'September':9,
        'October':10,
        'November':11,
        'December':12
    }

    month = dict[month];
    var cleanedTime = year+'-'+month+'-'+date+' '+time;

    console.log(cleanedTime);
    var file = document.getElementById("id_seatLayout")
    var files =file.files

    console.log($('#id_seatLayout').val())

    var dict = {
        name: $('#id_name').val(),
        description: $('#id_description').val(),
        location: $('#id_location').val(),
        time: cleanedTime,
        media: $('#id_media').val(),
        email: $('#id_email').val(),
        tickets_data: JSON.stringify(ticketsData),
        latitude: lat,
        longitude:long,
    }



    console.log(dict)
    var formdata = new FormData()
    formdata.append("seatLayout",file.files[0])
    formdata.append("name", $('#id_name').val())
    formdata.append("description", $('#id_description').val())
    formdata.append("time",cleanedTime)
    formdata.append("media", $('#id_media').val())
    formdata.append("email", $('#id_email').val())
    formdata.append("tickets_data", JSON.stringify(ticketsData))
    formdata.append("latitude", lat)
    formdata.append("longitude", long)


    jQuery.ajax({
              url: "/post-event",
              type: "POST",
              data: formdata,
              processData: false,
              contentType: false,
              success:function(){
                  window.location.href="/my-events"
              },
              fail:function(xhr, status, error)
              {
                  alert(xhr.responseText)
              }

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

  document.getElementById('id_location').addEventListener('focusout', function()
  {

     geocodeAddress(geocoder, map);

  }

);

}

function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('id_location').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {

        //global
        lat=results[0].geometry.location.lat()
        long=results[0].geometry.location.lng()


      resultsMap.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
      });
    } else {
      alert('Enter a valid location! ');
    }
  });
}

function setDateTimeSettings(){
    $(".form_datetime").datetimepicker({
        format: "dd MM yyyy - hh:ii"
    });
}

$(document).ready(function () {
    setCsrf();
    addClickHandlers();
    setDateTimeSettings();

});

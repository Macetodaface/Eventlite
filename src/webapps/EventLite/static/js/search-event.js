/**
 * Created by Chris Grabowski on 11/14/2016.
 */

// Map Stuff
window.initMap = function () {
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,
    center: {lat: -34.397, lng: 150.644}
  });

  var geocoder = new google.maps.Geocoder();
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

};

function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('id_location').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {

        //global
        lat=results[0].geometry.location.lat();
        long=results[0].geometry.location.lng();


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

});

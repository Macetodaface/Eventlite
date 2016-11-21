window.initMap = function ()
{

      var lati = document.getElementById('lat').value
      var long = document.getElementById('long').value

      var myLatLng = {lat: parseFloat(lati), lng: parseFloat(long)};

  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,
    center: {lat: parseFloat(lati), lng: parseFloat(long)}
    //center: {lat: -34.397, lng: 150.644}
  });

  var marker = new google.maps.Marker({
    map:map,
    position: myLatLng
  });


}

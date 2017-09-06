var map = L.map('map', {
  center:  [35.317, -0.527],
  zoom:    3,
  maxZoom: 12,
})

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map)

function userMarker(latlng, username, urlPath) {
  return L.marker(latlng, {
    title: username,
    alt:   username,
  }).bindPopup(`<a href="https://zestedesavoir.com${urlPath}" class="popup-link">${username}</a>`)
}

function getMarkersData(cb) {
  var httpReq = new XMLHttpRequest()
  httpReq.addEventListener('load', function() {
    cb(JSON.parse(this.responseText))
  })
  httpReq.open('GET', 'https://tleb.github.io/zds-user-map/markers.json', false)
  httpReq.send()
}

getMarkersData(function(markers) {
  var cluster = L.markerClusterGroup()
  cluster.addLayers(markers.map(m => userMarker(m.latlng, m.username, m.urlPath)))
  map.addLayer(cluster)
})

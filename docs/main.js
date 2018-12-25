const map = L.map('map', {
  center:  [35.317, -0.527],
  zoom:    3,
})

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map)

function userMarker(m) {
  return L.marker([m.lat, m.lon], {
    title: m.username,
    alt:   m.username,
  }).bindPopup(`<a href="${m.url}" class="popup-link">${m.username}</a>`)
}

function getMarkersData(cb) {
  const httpReq = new XMLHttpRequest()
  httpReq.addEventListener('load', function() {
    cb(JSON.parse(this.responseText))
  })
  httpReq.open('GET', 'https://tleb.github.io/zds-user-map/markers.json', true)
  httpReq.send()
}

getMarkersData(function(markers) {
  const cluster = L.markerClusterGroup()
  cluster.addLayers(markers.map(userMarker))
  map.addLayer(cluster)

  const controlSearch = new L.Control.Search({
    position: 'topright',
    layer: cluster,
    initial: false,
    zoom: 12,
    marker: false,
  })
  map.addControl(controlSearch)

  const querystring = window.location.href.split('?')[1] || ''

  // ignore '/?' and '/' cases
  if (querystring === '') return;

  // search the querystring
  controlSearch.searchText(querystring)

  // when something has been found, press enter
  // only happens once
  const observer = new MutationObserver(_ => {
    controlSearch._handleKeypress({ keyCode: 13 })
    observer.disconnect()
  })
  observer.observe(controlSearch._tooltip, { childList: true })

  // if the user searches something, we should disable the auto-enter
  document.querySelector('input').addEventListener('change', () => {
    observer.disconnect()
  })
})

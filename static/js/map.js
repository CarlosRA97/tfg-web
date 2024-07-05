// https://cloud.maptiler.com/maps/satellite/

var map = L.map("map").setView([37.2231, -4.7652], 7);
var tiles = L.tileLayer('https://api.maptiler.com/maps/satellite/{z}/{x}/{y}@2x.jpg?key=CBuOZswVx11ViZEsWDx0', {
    maxZoom: 19,
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
});

tiles.addTo(map)

var areaSelect = L.areaSelect({
    width: 224, 
    height: 224, 
    //keepAspectRatio:true,
    //minHorizontalSpacing: 80,
    //minVerticalSpacing: 80,
});


var selectorWidth = document.getElementById('width');
var selectorHeight = document.getElementById('height');

areaSelect.on("change", function() {
    var bounds = this.getBounds();
    document.querySelector("#result .sw").value = (bounds.getSouthWest().lat + ", " + bounds.getSouthWest().lng);
    document.querySelector("#result .ne").value = (bounds.getNorthEast().lat + ", " + bounds.getNorthEast().lng);
    document.querySelector(".width").value = (this.getDimensions().width);
    document.querySelector(".height").value = (this.getDimensions().height);
    selectorWidth.value = this.getDimensions().width;
    selectorHeight.value = this.getDimensions().height;
});
areaSelect.addTo(map);

selectorHeight.addEventListener("change", function(e) {
  areaSelect.setDimensions({"height": e.target.value})
})

selectorWidth.addEventListener("change", function(e) {
  areaSelect.setDimensions({"width": e.target.value})
})

const States = {
  loading: Symbol("loading"),
  ready: Symbol("ready"),
  ok: Symbol("ok"),
  error: Symbol("error")
}

addEventListener('#captureMap', (e) => {
  switch (e.detail.state) {
    case States.ready:
      document.querySelector(e.type).classList.remove('is-primary', 'is-danger', 'is-outlined')
      break;

    case States.loading:
      document.querySelector(e.type).classList.add('is-loading')
      break;

    case States.ok:
      document.querySelector(e.type).classList.remove('is-loading')
      document.querySelector(e.type).classList.add('is-primary', 'is-outlined')
      setTimeout(function () {
        emitState(e.type, States.ready)
      }, 500)
      break;

    case States.error:
      document.querySelector(e.type).classList.remove('is-loading')
      document.querySelector(e.type).classList.add('is-danger', 'is-outlined')
      setTimeout(function () {
        emitState(e.type, States.ready)
      }, 500)
      break;

    default:
      break;
  }
})

function emitState(id, state) {
  dispatchEvent(new CustomEvent(id, {detail: { state: state }}))
}

async function fetchWithTimeout(url, timeout = 4000) { // Default timeout of 1 second
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(id); // Clear timeout if fetch is successful
    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      emitState("#captureMap", States.error)
      console.error('Fetch request aborted due to timeout');
    } else {
      throw error; // Rethrow other errors
    }
  }
}

function captureMap() {
    const cropCanvas = (sourceCanvas,left,top,width,height) => {
        let destCanvas = document.createElement('canvas');
        destCanvas.width = width;
        destCanvas.height = height;
        destCanvas.getContext("2d").drawImage(
            sourceCanvas,
            left,top,width,height,  // source rect with content to crop
            0,0,width,height);      // newCanvas, same size as source rect
        return destCanvas;
    }
    emitState("#captureMap", States.loading)
    leafletImage(map, async function(err, canvas) {
        // now you have canvas
        // example thing to do with that canvas:

        var img = document.createElement('img');

        var dimensions = map.getSize();
        img.width = document.querySelector('.width').value;
        img.height = document.querySelector('.height').value;
        img.src = cropCanvas(canvas, (dimensions.x / 2) - (img.width / 2), (dimensions.y / 2) - (img.height / 2), img.width, img.height).toDataURL();
        const imgBlob = await fetch(img.src).then(response => response.blob())
        const byteArray = new Uint8Array(await imgBlob.arrayBuffer());

        fetch('/scan', {
            method: 'POST',
            headers: {
              'Content-Type': imgBlob.type, // adjust based on your image format
            },
            body: {
              "image": byteArray,
              "coords": areaSelect.getBounds(),
            }
          })
          .then(response => {
            // Handle the response
            if (response.ok) {
              console.log("Image posted successfully!");
              emitState("#captureMap", States.ok)
            } else {
              console.error("Error posting image:", response.statusText);
              emitState("#captureMap", States.error)
            }
          })
          .catch(error => {
            console.error("Error:", error);
            emitState("#captureMap", States.error)
          });
    });
}

// function to convert degrees to radians
function toRadians(degrees) {
  return (degrees * Math.PI) / 180;
}

// function to calculate the area of a polygon
function calculatePolygonArea(latlngs) {
  // Earth's radius in meters
  const R = 6378137;

  // number of points
  const pointsCount = latlngs.length;

  if (pointsCount < 3) return 0;

  let area = 0;

  for (let i = 0; i < pointsCount; i++) {
    let p1 = latlngs[i];
    let p2 = latlngs[(i + 1) % pointsCount];

    let lat1 = toRadians(p1.lat);
    let lon1 = toRadians(p1.lng);
    let lat2 = toRadians(p2.lat);
    let lon2 = toRadians(p2.lng);

    area += (lon2 - lon1) * (2 + Math.sin(lat1) + Math.sin(lat2));
  }

  area = (Math.abs(area) * (R * R)) / 2;

  return area;
}

function addSegmentation() {
  // layer group
  let layers = L.layerGroup().addTo(map);

  // polygon
  const polygonsArea = [
    [52.2303720513083, 21.01182227649689],
    [52.229590161561866, 21.010928342628483],
    [52.22930430472933, 21.012029091316227],
    [52.23008958517418, 21.01269364356995],
  ];

  // add polygon to layers
  const polygon = L.polygon(polygonsArea, { color: "red" }).addTo(layers);
  const polygonArea = calculatePolygonArea(polygon.getLatLngs()[0]);
  // add tooltip to marker
  polygon.bindTooltip("Area: " + polygonArea.toFixed(5) + " m²", {
    permanent: true,
    direction: "bottom",
    className: "area",
    offset: [-15, 30],
  });
}

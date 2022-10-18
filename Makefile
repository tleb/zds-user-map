ESBUILD_PATH ?= node_modules/.bin/esbuild

.PHONY: all clean
all: docs/leaflet-and-co.css docs/leaflet-and-co.js docs/images

clean:
	rm -f docs/leaflet-and-co.{css,js}
	rm -rf docs/images

docs/leaflet-and-co.css: node_modules/leaflet/dist/leaflet.css \
		node_modules/leaflet.markercluster/dist/MarkerCluster.css \
		node_modules/leaflet.markercluster/dist/MarkerCluster.Default.css \
		node_modules/leaflet-search/dist/leaflet-search.min.css
	for f in $^; do (cat $$f; echo); done \
	| $(ESBUILD_PATH) --loader=css --minify \
	| cat <(cat leaflet-prefix.txt) - \
	> $@

docs/leaflet-and-co.js: node_modules/leaflet/dist/leaflet.js \
		node_modules/leaflet.markercluster/dist/leaflet.markercluster.js \
		node_modules/leaflet-search/dist/leaflet-search.src.js
	for f in $^; do (cat $$f; echo); done \
	| $(ESBUILD_PATH) --minify \
	| cat <(cat leaflet-prefix.txt) - \
	> $@

docs/images: node_modules/leaflet/dist/images
	cp -r $^ $@

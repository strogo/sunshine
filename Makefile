dem_file="http://viewfinderpanoramas.org/dem3/I28.zip"
clip=-17.31468940932131 32.971719119503696 -16.605152503283087 32.53908237708143
proj=EPSG:3061
resolution=5
sunshine_resolution=50
contour_step=100

sources_dir=sources
demzip=${sources_dir}/dem/dem.zip

process_dir=layers
process_dir_dem=${process_dir}/dem

clean:
	rm -rf $(sources_dir)
	rm -rf $(process_dir)

$(demzip):
	mkdir -p `dirname $(demzip)`
	wget -c $(dem_file) -O $(demzip)

sources: $(demzip)
	echo "Done"

# $(process_dir_dem)/.tmp/clipped.tiff: $(demzip)
$(process_dir_dem)/dem.tiff $(process_dir_dem)/dem_sunshine.tiff: $(demzip)
	mkdir -p $(process_dir_dem)/.tmp
	unzip -o $(demzip) -d $(process_dir_dem)/.tmp
	gdal_merge.py -o $(process_dir_dem)/.tmp/merged.tiff $(process_dir_dem)/.tmp/*/*.hgt
	gdal_translate -projwin $(clip) -of GTiff $(process_dir_dem)/.tmp/merged.tiff $(process_dir_dem)/.tmp/clipped.tiff
	gdalwarp -t_srs $(proj) -tr $(resolution) $(resolution) -r cubicspline -multi -ot Float32 -of GTiff $(process_dir_dem)/.tmp/clipped.tiff $(process_dir_dem)/dem.tiff
	gdalwarp -t_srs $(proj) -tr $(sunshine_resolution) $(sunshine_resolution) -r cubicspline -multi -ot Float32 -of GTiff $(process_dir_dem)/.tmp/clipped.tiff $(process_dir_dem)/dem_sunshine.tiff
	rm -rf $(process_dir_dem)/.tmp

$(process_dir_dem)/contour.shp: $(process_dir_dem)/dem.tiff
	gdal_contour -b 1 -a ELEV -i $(contour_step) -f "ESRI Shapefile"  $(process_dir_dem)/dem.tiff $(process_dir_dem)/contour.shp

$(process_dir_dem)/ruggedness.tiff: $(process_dir_dem)/dem.tiff
	gdaldem TRI $(process_dir_dem)/dem.tiff $(process_dir_dem)/ruggedness.tiff

$(process_dir_dem)/hillshade.tiff: $(process_dir_dem)/dem.tiff
	gdaldem hillshade $(process_dir_dem)/dem.tiff $(process_dir_dem)/hillshade.tiff -of GTiff -b 1 -z 1.0 -s 1.0 -alt 45.0

process: sources $(process_dir_dem)/dem.tiff $(process_dir_dem)/contour.shp $(process_dir_dem)/ruggedness.tiff $(process_dir_dem)/hillshade.tiff


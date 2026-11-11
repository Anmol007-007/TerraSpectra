# Day 4 — GeoTIFF/HDF5 IO, reader abstractions, windowed IO, GDAL helpers; farm layers

Goal: Rasterio/h5py ingestion with memory-safe windows and GDAL utilities; farm boundary layers on map.

**Branch:** `day/04-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Writers

- [ ] **01** `feat(data): add GeoTIFF multi-band writer using rasterio`
- [ ] **02** `feat(data): set CRS and affine transform on written GeoTIFF`
- [ ] **03** `feat(data): write wavelength band descriptions and tags`
- [ ] **04** `feat(data): set nodata value -9999`
- [ ] **05** `feat(data): add tiled and compressed GeoTIFF profile`
- [ ] **06** `feat(data): add HDF5 chunked cube writer with h5py`
- [ ] **07** `feat(data): write HDF5 attributes wavelengths crs transform`
- [ ] **08** `feat(data): add label and DEM raster writers`
- [ ] **09** `test(data): add GeoTIFF round-trip test`
- [ ] **10** `test(data): add HDF5 round-trip test`

## B. Reader abstractions

- [ ] **11** `feat(data): add CubeReader abstract base class`
- [ ] **12** `feat(data): add GeoTiffReader`
- [ ] **13** `feat(data): add Hdf5Reader`
- [ ] **14** `feat(data): add reader factory by file extension`
- [ ] **15** `feat(data): add scene metadata extraction`
- [ ] **16** `feat(data): add wavelength parsing from tags and attrs`
- [ ] **17** `feat(data): add CRS validation and warnings`
- [ ] **18** `feat(data): add window read method`
- [ ] **19** `feat(data): add lazy band-chunk iterator`
- [ ] **20** `test(data): add reader parity tests between formats`

## C. Memory-safe windowed IO

- [ ] **21** `feat(data): add block window iterator`
- [ ] **22** `feat(data): add overlapping window iterator`
- [ ] **23** `feat(data): add memory estimation for cube and window`
- [ ] **24** `feat(data): add auto chunk size selection from RAM budget`
- [ ] **25** `feat(data): add band-subset read support`
- [ ] **26** `feat(data): add resampled read with out_shape`
- [ ] **27** `feat(data): add small LRU window cache`
- [ ] **28** `test(data): add property test that windows cover raster exactly`

## D. GDAL helpers

- [ ] **29** `feat(geo): add gdalinfo wrapper returning dict`
- [ ] **30** `feat(geo): add reproject helper`
- [ ] **31** `feat(geo): add warp to common grid`
- [ ] **32** `feat(geo): add VRT mosaic builder`
- [ ] **33** `feat(geo): add COG conversion helper`
- [ ] **34** `feat(geo): add clip raster to polygon`
- [ ] **35** `feat(geo): add GSD resampling helper`
- [ ] **36** `test(geo): add tests on tiny rasters`

## E. Frontend farm layers

- [ ] **37** `feat(web): add mock farm boundary GeoJSON`
- [ ] **38** `feat(web): add farmBoundary GeoJsonLayer`
- [ ] **39** `feat(web): add parcels GeoJsonLayer`
- [ ] **40** `feat(web): add fly-to-farm camera action`
- [ ] **41** `feat(web): add fitBounds utility`
- [ ] **42** `feat(web): add layer registry`
- [ ] **43** `feat(web): add layer visibility state slice`
- [ ] **44** `feat(web): add basemap attribution`
- [ ] **45** `test(web): add fitBounds tests`
- [ ] **46** `docs(web): document layer registry usage`

## F. Scene catalog

- [ ] **47** `feat(data): add SceneCatalog model`
- [ ] **48** `feat(data): add directory scanner for scenes`
- [ ] **49** `feat(data): write catalog JSON`
- [ ] **50** `feat(cli): add catalog command`
- [ ] **51** `test(data): add catalog tests`
- [ ] **52** `docs: update data spec with catalog format`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/04-work` into `main` with `--no-ff`.

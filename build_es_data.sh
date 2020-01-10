#!/usr/bin/env bash
echo
echo =================================
echo === I. ETL strains to ES ========
echo

python3 manage.py etl_strains_to_es --drop_and_rebuild --index=STRAIN

echo
echo === II. Build strain rating ES ==
echo

python3 manage.py build_strain_rating_es_index --drop_and_rebuild --index=USER_RATINGS

echo
echo === III. Build locations ES =====
echo

python3 manage.py build_bus_locations_es_index --drop_and_rebuild --index=BUSINESS_LOCATION

echo
echo === ES building has been DONE ===
echo =================================
echo

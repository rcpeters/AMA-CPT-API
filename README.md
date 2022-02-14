# AMA-CPT-API

Currently this repo is an example python client of AMA's CPT API, [CPTAPI_Zip](https://platform.ama-assn.org/ama/#/devportal/portal/api). As of version 1.0.0 CPTAPI_Zip (Feb 2022) the releases.json doesn't provide a reliable pointer to which CPT Zip is returned. For example there are releases with dates in the future in the releases.json. Regardless, we should celebrate the step forward for AMA CPT. To overcome the 1.0.0 issues the script does the following:

* The API's HTTP response Last-Modified date is read and compared to the local copy of the cpt zip file. If the last modified is newer new CPT zip file is downloaded.

* The contents of the file are inspected for the published date is used in the file structure. The file will be written with  this date date in it's name when persisted to local disk. For instance ```"ama_cpt_" + cpt_pub_date + ".zip"```

* A hard link called ```ama_cpt_latest.zip``` is created and points to the latest CPT Zip downloaded to the disk.

This script should just be considered chicken scratch. If are interested in a more robust script or a script in another language please feel free to contact me as I'm looking to pick up projects.

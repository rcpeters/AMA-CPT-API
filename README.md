# AMA-CPT-API

Currently this repo just has an example python use of AMA's CPT API, [CPTAPI_Zip](https://platform.ama-assn.org/ama/#/devportal/portal/api). As of version 1.0.0 CPTAPI_Zip the releases.json doesn't match in a clear way which CPT Zip is returned. To overcome this:

* The API's HTTP reponse Last-Modified date is read and compared to the local copy of the cpt zip file.

* The contents of the file are inspected for the published date is used in the file structure. The file has this date included it's name when persisited to local disk. For instance ```"ama_cpt_" + cpt_pub_date + ".zip"```

* A hard link called ```ama_cpt_latest.zip``` is created and points to the latest CPT Zip download download.

This scirpt should just be considered chicken scratch. If are insterested in a more robust script or a script in another language please feel free to contact me.

# Extraction Pipeline

## Overview
Extraction pipeline is a comprehensive suite of tools customly created to extract valuable data from various document formats, including PDF, DOCX, XML, and JSON.
The extraction pipeline supports both *Batch* processing for a one-time extraction and *Continuous* processing to monitor a Google Cloud Storage bucket for new files and extract data at specified intervals.
In Batch mode all the files in given directory or gs bucket are processed at once. 
In Continuous mode the pipeline processes files in given bucket and then checks the bucket every set time if new files were added. If so, the files are processed and copied into given output bucket or datastore.

## Usage
There are three parameters you need to pass to run the pipeline:
- **mode** - it can be either `batch` or `continuous` (Required argument)
- **input** - input directory or gs bucket directory where input files are located (Required argument)
- **output** - output directory in local system, GCS bucket path or Datastore ID. Default is `output_data`.

```sh
python gen_ai/extraction_pipeline/processor.py <mode> -i <input> -o <output>
```

## Batch mode
Batch mode can process both local directories and GCS buckets. And the result can be uploaded to the GCS bucket automatically or datastore can be updated through BQ table if necessary. Arguments you need to pass are `mode` and `input`. If no `output` is provided, default value is "output_dir" which is created automatically. Input directory can be local directory or GCS bucket directory.

## Continuous mode
Continuous mode processes GCS buckets only, it first processes all the files in the input directory. Afterwards it checks the bucket every 10 minutes if new files were added. If so, it processes new files and transfer them to the destination GCS bucket or updates datastore through BQ table. Arguments you need to pass are `mode`, `input` (bucket address) and `output` where processed files will be uploaded.

## Config file

The configuration file of which type of extraction to use for each file type is in `config.yaml`, inside *'extraction_pipeline'* directory. For each type of file there are two parameters: `Extraction` and `Chunking`. If no value is given in config file, "default" is used as the value.

## Examples
*Batch processing of a local directory*
```sh
python gen_ai/extraction_pipeline/processor.py batch -i /mnt/resources/dataset/main_folder -o output_dir
```

*Batch processing of a GCS Bucket and GCS Bucket output*
```sh
python gen_ai/extraction_pipeline/processor.py batch -i gs://dataset_raw_data/extractions -o gs://dataset_clean_data
```

*Continuous processing of a GCS bucket and Datastore output*
```sh
python gen_ai/extraction_pipeline/processor.py continuous -i gs://dataset_raw_data/20240417_docx -o datastore:datastore_id
```
## Installation
1. Update the package list and Install the dependencies
```sh
sudo apt-get update && sudo apt-get install libgl1 poppler-utils tesseract-ocr
```
2. Install the python requirements  
Update the line 13 in `setup.py` file to: `install_requires=get_requirements("gen_ai/extraction_pipeline/requirements.txt"),`  
Then run pip install:
```sh
pip install -e .
```


## Important Notes
- Ensure that the `config.yaml` file is correctly configured with the required parameters.
- For GCS operations, make sure you have the necessary permissions to access the buckets.
- In continuous mode, the script will run indefinitely, monitoring the GCS bucket for new files.


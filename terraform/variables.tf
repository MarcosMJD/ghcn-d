variable "DATA_LAKE_BUCKET" {
  description = "Name of the data lake in GCS where to store the raw files"
  default = "ghcnd_raw"
  type = string
}

variable "PROJECT" {
  default = "ghcn-d"
  description = "Global Historical Climatology Network Daily Data Engineering"
}

variable "REGION" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "europe-west6"
  type = string
}

variable "STORAGE_CLASS" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "ghcnd"
}
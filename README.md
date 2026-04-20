# azure-aws-connector

A lightweight HTTP service that transfers files from **Azure Data Lake Storage Gen2** to **AWS S3**. You send API call with the source and destination details, and the service downloads the file from Azure and uploads it to S3.

## How it works


The file is staged temporarily in a local folder (configurable via `DATA_FOLDER`) and deleted immediately after the S3 upload completes.

---

## Requirements

- Docker, or Python 3.x if running locally
- An Azure Storage account with Data Lake Storage Gen2 enabled
- An AWS S3 bucket

---

## Running with Docker

Pull and run the published image:

```bash
docker run -d \
  -p 8000:8000 \
  -e DATA_LAKE_SAS="your-sas-token" \
  -e AWS_ACCESS_KEY_ID="your-key-id" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-key" \
  sunmaungoo/azure-aws-connector:latest
```

Or build it yourself:

```bash
docker build -t azure-aws-connector .
docker run -d -p 8000:8000 \
  -e DATA_LAKE_SAS="your-sas-token" \
  -e AWS_ACCESS_KEY_ID="your-key-id" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-key" \
  azure-aws-connector
```

## Running locally

```bash
pip install -r requirements.txt
export DATA_LAKE_SAS="your-sas-token"
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
python src/app.py
```

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATA_LAKE_SAS` | Yes | — | Azure SAS token for the Data Lake (see [Azure permissions](#azure-permissions) below) |
| `AWS_ACCESS_KEY_ID` | Yes | — | AWS access key ID (see [AWS permissions](#aws-permissions) below) |
| `AWS_SECRET_ACCESS_KEY` | Yes | — | AWS secret access key |
| `DATA_FOLDER` | No | `data` | Local folder used to stage the downloaded file before upload |
| `HOST` | No | `127.0.0.1` | Host address the server binds to |
| `PORT` | No | `8000` | Port the server listens on |

---

## API

### `POST /transfer/s3`

Downloads a file from Azure Data Lake and uploads it to S3.

**Request body (JSON):**

| Field | Type | Description |
|---|---|---|
| `azure_storage_account` | string | Name of the Azure Storage account |
| `azure_container` | string | Container (filesystem) name in Data Lake |
| `azure_folder_path` | string | Folder path inside the container, e.g. `folder/subfolder` |
| `azure_file_name` | string | File name to download, e.g. `report.csv` |
| `s3_bucket` | string | Destination S3 bucket name |
| `s3_folder_path` | string | Destination folder path in S3, e.g. `output/reports` |
| `s3_file_name` | string | File name to use in S3, e.g. `report.csv` |

**Example request:**

```bash
curl -X POST http://localhost:8000/transfer/s3 \
  -H "Content-Type: application/json" \
  -d '{
    "azure_storage_account": "mystorageaccount",
    "azure_container": "my-container",
    "azure_folder_path": "folder/subfolder",
    "azure_file_name": "report.csv",
    "s3_bucket": "my-s3-bucket",
    "s3_folder_path": "output/reports",
    "s3_file_name": "report.csv"
  }'
```

**Success response (200):**

```json
{
  "message": "Upload successful",
  "s3_path": "output/reports/report.csv"
}
```

**Error responses:**

| Status | Cause |
|---|---|
| `422` | Missing or invalid request fields |
| `500` | Failed to download from Azure Data Lake |
| `500` | Failed to upload to S3 |

---

## Azure permissions

The service authenticates to Azure using a **SAS token** passed via `DATA_LAKE_SAS`. The token is used for every request and must be scoped to the storage account level (not a single container), since the container name is supplied per API call.

The SAS token requires the minimum permissions below. No other permissions are needed.

| Permission | Why it is needed |
|---|---|
| **Read** | Download the file content from the Data Lake |
| **List** | Traverse the directory path to reach the target file |


---

## AWS permissions

The service authenticates to S3 using a static **access key** (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`). The IAM user or role behind these credentials needs only the single S3 action below.

| Permission | Why it is needed |
|---|---|
| `s3:PutObject` | Upload the file to the destination bucket |

---

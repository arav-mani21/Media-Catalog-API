# Media Catalogue API

A RESTful API for managing a catalogue of books and movies, built with FastAPI and backed by AWS DynamoDB. Infrastructure is provisioned and managed entirely through Terraform.

This project was built to strengthen hands-on skills in two areas:
- **Application development** with FastAPI — routing, request/response validation via Pydantic, and clean separation of concerns
- **Infrastructure management** with Terraform — provisioning AWS resources, writing IAM policies, and automating EC2 deployment

---

## Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| API Framework  | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Database       | AWS DynamoDB (via boto3)            |
| Infrastructure | Terraform                           |
| Compute        | AWS EC2 (t2.micro, free tier)       |

---

## Architecture

```
                        ┌─────────────────────────────┐
                        │        AWS EC2 (t2.micro)    │
                        │                              │
  HTTP :8001            │   ┌──────────────────────┐   │
 ─────────────────────► │   │   FastAPI (Uvicorn)   │   │
                        │   │                      │   │
                        │   │  /books   /movies    │   │
                        │   └──────────┬───────────┘   │
                        │              │ boto3          │
                        └─────────────────────────────-┘
                                       │
                          IAM Role     │
                          (DynamoDB    ▼
                           access)  ┌──────────────────┐
                                    │  AWS DynamoDB     │
                                    │  ┌─────────────┐ │
                                    │  │ books table │ │
                                    │  └─────────────┘ │
                                    │  ┌──────────────┐ │
                                    │  │ movies table │ │
                                    │  └──────────────┘ │
                                    └──────────────────┘

Terraform provisions: EC2, DynamoDB tables, Security Group, IAM Role + Policy, Key Pair
```

---

## Project Structure

```
media_catalogue_api/
├── app/
│   ├── main.py             # FastAPI app entry point, router registration
│   ├── models.py           # Pydantic models (Book, Movie, *Base, *Create)
│   ├── database.py         # DynamoDB client and CRUD operations
│   ├── requirements.txt    # Python dependencies
│   └── routes/
│       ├── books.py        # /books endpoints
│       └── movies.py       # /movies endpoints
│
├── terraform/
│   ├── main.tf             # AWS resource definitions
│   ├── variables.tf        # Input variables (region, AMI, instance type)
│   └── outputs.tf          # Output values (EC2 IP, table ARNs)
│
│
└── user_data.sh            # EC2 bootstrap script (installs app, creates systemd service)
```

---

## API Reference

Both resources share the same CRUD shape. Replace `/books` with `/movies` for the movies endpoints.

### Books

| Method   | Endpoint        | Description              | Status Codes    |
|----------|-----------------|--------------------------|-----------------|
| `POST`   | `/books/`       | Create a new book        | 201, 422        |
| `GET`    | `/books/`       | List all books           | 200             |
| `GET`    | `/books/{id}`   | Get a book by ID         | 200, 404        |
| `PUT`    | `/books/{id}`   | Update a book by ID      | 200, 404        |
| `DELETE` | `/books/{id}`   | Delete a book by ID      | 200, 404        |

### Movies

| Method   | Endpoint        | Description              | Status Codes    |
|----------|-----------------|--------------------------|-----------------|
| `POST`   | `/movies/`      | Create a new movie       | 201, 422        |
| `GET`    | `/movies/`      | List all movies          | 200             |
| `GET`    | `/movies/{id}`  | Get a movie by ID        | 200, 404        |
| `PUT`    | `/movies/{id}`  | Update a movie by ID     | 200, 404        |
| `DELETE` | `/movies/{id}`  | Delete a movie by ID     | 200, 404        |

### Request / Response Schemas

**Book / Movie body (POST, PUT):**
```json
{
  "title": "string",
  "author": "string",      // books only
  "director": "string",    // movies only
  "genre": "string",
  "year": 0
}
```

**Response includes a generated `id`:**
```json
{
  "id": "uuid-string",
  "title": "string",
  "author": "string",
  "genre": "string",
  "year": 0
}
```

Interactive docs are available at `http://<host>:8001/docs` when the app is running.

---

## Running the Application

There are two ways to run this project, depending on your goal.

| | Run Locally | Deploy to AWS |
|---|---|---|
| **FastAPI runs on** | Your machine | EC2 instance |
| **DynamoDB** | AWS (remote) | AWS (remote) |
| **Auth to DynamoDB** | Local AWS credentials | EC2 IAM role (no credentials needed) |
| **Use case** | Development, testing | Production-like deployment |

---

## Option 1: Run Locally

The FastAPI app runs on your machine, but DynamoDB still lives in AWS — so you need AWS credentials configured locally. The DynamoDB tables must already exist (provisioned via Terraform or created manually).

### Prerequisites

- Python 3.9+
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- DynamoDB `books` and `movies` tables provisioned in `us-east-1`

### Setup

```bash
# Clone the repository
git clone https://github.com/arav-mani21/Media-Catalog-API.git
cd Media-Catalog-API

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt
```

### Run the API

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at `http://localhost:8001`.

---

## Option 2: Deploy to AWS

This is the full cloud deployment. Terraform provisions all infrastructure (EC2, DynamoDB, IAM, networking), and the EC2 instance bootstraps itself on launch via `user_data.sh` — no manual setup on the server required.

The EC2 instance is assigned an IAM role that grants it DynamoDB access directly, so no AWS credentials need to be stored on the instance.

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) installed
- AWS credentials configured locally (used by Terraform to provision resources)
- An SSH public key at `~/.ssh/id_rsa_ec2.pub`

### AWS Resources Provisioned

| Resource                  | Details                                                |
|---------------------------|--------------------------------------------------------|
| `aws_dynamodb_table`      | `books` and `movies` tables, PAY_PER_REQUEST billing   |
| `aws_instance`            | Amazon Linux 2, t2.micro (free tier), port 8001 open   |
| `aws_security_group`      | Allows inbound SSH (22) and API traffic (8001)         |
| `aws_key_pair`            | SSH key pair for EC2 access                            |
| `aws_iam_role`            | EC2 instance role with DynamoDB access policy attached |

### Provision and Deploy

```bash
cd terraform

# Initialize providers
terraform init

# Preview what will be created
terraform plan

# Provision all resources and launch the EC2 instance
terraform apply
```

Once `apply` completes, Terraform outputs the EC2 public IP:

```bash
terraform output fastapi_server_public_ip
```

The API will be available at `http://<fastapi_server_public_ip>:8001`.

> The EC2 instance runs `user_data.sh` on first boot, which clones the app from GitHub, sets up a Python virtual environment, and registers it as a `systemd` service. Allow 1-2 minutes after provisioning for the service to come up.

### Verify the Deployment

SSH into the instance to check the service status:

```bash
ssh -i ~/.ssh/id_rsa_ec2 ec2-user@<fastapi_server_public_ip>
sudo systemctl status media_catalog
```

### Tear Down

```bash
terraform destroy
```

---
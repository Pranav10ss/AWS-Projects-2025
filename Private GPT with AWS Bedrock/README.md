# Private GPT with AWS Bedrock (Serverless RAG Application)
This project demonstrates how to build a serverless AI chat application using Amazon Bedrock Knowledge Bases.
The application allows users to interact with a private GPT-style chatbot powered by Retrieval Augmented Generation (RAG).

In this implementation, the chatbot is designed to assist with AWS Certified Solutions Architect – Professional (SAP-C02) exam preparation.
However, the same architecture can be adapted for any private knowledge base or organizational data.

[![AWS](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 🏗️ Architecture Overview
![Diagram explaining the architecture of this project](images/Architecture-diagram.svg)

The solution uses the following AWS Services:
* **Amazon Bedrock Knowledge Base** - Managed RAG implementation
* **Amazon S3** - Source data storage and vector store
* **Amazon API gateway** - Exposes the backend API. HTTP API with CORS enabled.
* **AWS Lambda** - Backend logic for querying the knowledge base
* **Amazon CloudFront** - CDN for frontend delivery
* **Amazon S3(static website hosting)** - HTML, CSS and JavaScript chat interface hosted on S3 + CloudFront
* **Terraform** - Infrastructure as Code(IaC)

## 📚 Retrieval Augmented Generation (RAG) Overview
Amazon Bedrock knowledge bases is a fully managed capability that simplifies the implementation of Retrieval Augmented Generation (RAG).
RAG enables foundational models to use up-to-date & proprietary organizational data to generate more accurate, grounded and context specific response. 

How RAG works in this Project:
1. **Document ingestion**
    - Source documents(PDFs) are stored in an Amazon S3 bucket.
    - In this project, the AWS Certified Solutions Architect - Professional (SAP-C02) exam guidelines PDF downloaded from the AWS website is used. Basically this PDF is an exam study guide for clearing the AWS certified Solutions Architect - Professional exam.
2. **Chunking & Embeddings**
   - The document is parsed, Chunked into smaller text segments and converted into numerical representations called **embeddings**.
   - An embedding model (Amazon Titan Embeddings G1 – Text) is used.
3. **Vector storage**
   - The embeddings and corresponding text chunks are stored in an Amazon S3 Vector store.
4. **Query Processing**
    * When a user asks a question:
        - The knowledge base retrieves the most relevant chunks from the vector store
        - The retrieved context is injected into the prompt
         - The enriched prompt is sent to the foundation model
        - The model generates a grounded response using the retrieved context
This ensures that the chatbot answers questions relevant to the provided knowledge base.

## Phase 1: Create the Knowledge Base (Console setup)
Create an Amazon bedrock knowledge database, store the data in the source S3 bucket. The data(PDF) will be converted into embeddings. 

### step 1: Request Model Access
* Open the AWS console, Go to **Amazon Bedrock** → **Model Catalog** → Request access for the model to use for this particular architecture.
* I requested the access for Anthropic Claude 3 Haiku. 
After few minutes, a mail from AWS will be received confirming the access to use the requested model.

### step 2: Upload Source Data
* Create an S3 bucket to hold the source data
* Upload the SAP-C02 exam guide PDF or any data/files that you want to use as the source file

### step 3: Create the knowledge base
* Go to **Amazon Bedrock** → **Build** → **Knowledge bases**.
* Configuration:
  - Knowledge base type: Unstructured data
  - Data source: Amazon S3
  - Parsing strategy: Amazon Bedrock default parser
  - Chunking strategy: Default
  - Embedding model: Amazon Titan Embeddings G1 – Text
  - Inference type: On-demand
  - Vector store: Amazon S3 vectors
  - IAM role: Create a new service role (for first-time users)

Once created, **sync** the data source to generate the embeddings and populate the S3 vector database.

##
**Test the Knowledge Base**:
After syncing, test the knowledge base directly from the console.
Example queries:
```
What are you capable of?
```
```
What skills are required to pass the SAP-C02 exam?
```
```
What's the minimum marks needed to pass the exam?
```
Expected behavior:
> The model politely refuses to answer questions outside the provided knowledge base, ensuring strict scope control.

##
## Phase 2: Build and deploy the application
In this phase, the knowledge base is exposed through a serverless API and a web frontend.

### Frontend Hosting
* Static frontend hosted on Amazon S3
* Served globally using Amazon Cloudfront
* API endpoint is injected dynamically using Terraform

### Backend Flow
1. User interacts with the frontend (served via CloudFront)
2. Frontend sends a request to API Gateway
3. API Gateway invokes a Lambda function
4. Lambda queries the Amazon Bedrock Knowledge Base
5. Response is returned to the frontend

### Project structure
```
.
├── terraform/
│   ├── main.tf           # Main infra configuration
│   ├── variables.tf      
│   ├── outputs.tf        
|   └── template.tf       # Generates frontend config.js from API Gateway URL
├── lambda/
│   ├── index.py          # Lambda function code
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Chat interface
│   ├── styles.css        # Styling
│   ├── app.js            # Frontend logic
|   └── config.js         # Generated config with API endpoint (do not hardcode)
└── README.md
```

### Configuration
* **Terraform Variables**
  - Update the `terraform/variables.tf` with the **Knowledge Base ID** and **Bedrock Model ID**.
The Model ID for any specific foundation model can be found in [this](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) documentation.

* The Lambda function uses the following Environment Variables:
  - KNOWLEDGE_BASE_ID
  - BEDROCK_MODEL_ARN

* **Custom System Instructions**: The Lambda function includes system instructions that guide the AI's behavior. We can customize these by editing the `system_instruction` variable in `lambda/index.py` to match any use case:

```python
system_instruction = """You are an expert assistant for [YOUR DOMAIN].
Your role is to:
1. Provide accurate information based on the knowledge base
2. [Add your specific requirements]
3. [Customize behavior as needed]
"""
```

## Usage
1. Get the frontend URL from the Cloudfront distribution under `Distribution domain name` and open it in a web browser.
2. Type the questions about the SAP-C02 exam
3. Click 'Send' or press Enter
4. View the AI-generated response with citations

### Example questions to ask
* "What is the score required to pass the AWS SAP-C02 exam?"
* "What are the main concepts covered in the SAP-C02 exam?"
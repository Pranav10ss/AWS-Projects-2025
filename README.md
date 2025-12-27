# Private GPT with AWS Bedrock
This project demonstrates on how to build a serverless AI chat application that allows users to interact with an AWS Bedrock knowledge base. We will build a private GPT-style chatbot for the AWS Certified DevOps Engineer - Professional(DOP-C02) exam preparation, but can be adapted for any knowledge base content.

* A knowledge base for amazon bedrock is fully managed capability that simplifies the process of implementing RAG(Retreival augmented generation). RAG is a technique that empowers foundational models to use up-to-date & proprietory organizational data to generate more relevant, accurate and context specific response. 
  - First it will automatically fetch the document from the data source(stored in S3 in the format of PDF). In this demonstration I will use AWS Certified DevOps Engineer - Professional (DOP-C02) exam guidelines PDF downloaded from the AWS website(basically this is a exam study guide for clearing the AWS certified DevOps Engineer - Professional exam). This PDF will be uploaded to the source bucket. 
  - Whenever we need to process it, basically it will chunk the entire document & convert the text into numerical representation into something called as **embedding**. It is going to use a specified embedding model(such as Claude Sonnet 4.5). It stores these embeddings and the original text snippets in the vector database(S3 vector buckets) that we use. The PDF will be converted into embeddings and it will be stored in the vector database. 
  - Whenever the user asks a question, the knowledge base first retreives the most relevant information from the vector store based on the user's query & then it enriches the original prompt with the retreived context & sends it to the foundational modelb for final grounded response. 

## Phase - 1
Create an Amazon bedrock knowledge database, store the data in the source S3 bucket. The data(PDF) will be converted into embeddings. Use a model(claude sonnet) to access and interact with the model.
### step - 1
In the AWS console, Go to amazon bedrock → Model Catalog → Request access for the model to use for this particular architecture.

### step - 2
Create an S3 bucket to hold the source data and upload the PDF.

### step - 3
Create the knowledge base and use the model. Go to Amazon Bedrock → Build → Knowledge bases.
Click create → unstructured dat(since the PDF is a unstructured data) → select Knowledge base with vector store → add a name → Create a IAM service role since the knowledge has to interact with bedrock foundational model & retreive the vector database. For the new users we'll have to create the new service role.

Choose the data source as S3 → choose the S3 bucket → select the parsing strategy as Amazon bedrock default parser → select the chucking strategy(text will be converted to numerical charecters) as default chunking.

Select the embedding model as Amazon Titan Embeddings G1 - Text → select the inference as on-demand.

Vector store: Quick create a new vector store and choose Amazon S3 vectors. Click on create knowledge base. 

### 
Once the knowledge base is created, the data source will also be created. Whatever the data is stored, should be synced with the vector database. So, select the data source and click on sync. Once the synced it will convert the entire data into embeddings and store that in the S3 vector database.

### Test the knowledge base
Click on Test the knowledge base → selct the foundation model and click on apply. 

We can start asking questions at this point.

```
What are you capable of ?
```

```
What are the skills required to pass the exam ?
```

```
Can you talk about AWS Network Speciality exam ?
# returns answer like "Sorry, I am unable to assist you with this request."
# We are limiting the knowledge of the foundation model to only answer what we have stored in the S3 source bucket.
```

## Phase - 2
### Build a frontend application and deploy on AWS
Create a Lambda function which will inturn talks to the API gateway. Whenever the user requests the frontend application which is powered by the cloudfront CDN(histed on s3 static website) . The API gateway will talk to the lambda function & the lambda function will talk to the Amazon bedrock KB and Lambda function will inturn speak to the bedrock KB and retreive the information and get the response from the model and give it back to the user.

When we run the `deploy.sh`, the script that we have(under Lambda folder) written to run on the lambda function will be zipped and run on Lambda.


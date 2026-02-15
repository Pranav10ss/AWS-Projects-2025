# End-to-End Data Pipeline on AWS to process CSV files using S3, Lambda, Glue & QuickSight
## Project Overview
In this project we'll build a serverless data pipeline on AWS for processing CSV files. 
The pipeline automates the ingestion, transformation, & visualization of data. 
CSV files are uploaded to an S3 bucket(*csv-raw-data*), which triggers a Lambda function to preprocess the data & store it in the processed data bucket(*csv-processed-data*).

AWS Glue is then used to ETL(Extract, Transform and Load) operations, and the final data is stored in a separate S3 bucket(*csv-final-data*). 
At last, Amazon QuickSight is used to create interactive dashboards & reports for visualizing the final data.

## Architecture
![Diagram explaining the architecture of this project](images/Architecture-diagram.svg)
### Services used in this project
* **Amazon S3**: Used for storing raw and processed data, which also provides event-driven architecture capabilities with S3 event notifications.
* **AWS Lambda**: Acts as a serverless compute service, which gets automatically triggered to pre-processes or clean CSV files upon upload to S3.
* **AWS Glue**: Provides ETL capabilities to extract, transform and load data into a usable format for analysis.
* **Amazon QuickSight**: Offers interactive dashboards and reports for real-time data visualization.
* **IAM**: IAM Roles and Policies ensures secure access to S3, Lambda, Glue and QuickSight.

### Stages 
1. A raw CSV file uploaded to the *csv-raw-data* S3 bucket, initiates the pipeline.
2. A **Lambda function** is automatically triggered to read & pre-process the uploaded CSV file.
3. The Lambda function filters/formats data & stores the cleaned files in the *csv-processed-data* S3 bucket.
4. **AWS Glue Crawler** scans the processed data and identifies its schema for further processing.
5. The Glue Crawler updates the **AWS Glue Data Catalog** and creates a structured table for ETL operations.
6. **Source** → **Transform** → **Store**. 
Glue Job extracts data from table created in Glue Data Catalog, transforms it and loads the final output into the *csv-final-data* S3 bucket.
7. We'll be utilizing **Amazon QuickSight** which connects the final data set enabling interactive dashboards and reports for data visualization.

## Steps to implement this project
### Step 1: Initial Setup and Configuration
1. **Create the S3 bucket**
    * Create three S3 buckets for storing *raw*, *processed* and *final* data respectively.
Keep the name of the S3 buckets unique, such as *csv-raw-data*, *csv-processed-data* and *csv-final-data*. 
      - In the *csv-raw-data* bucket, created a folder called `raw/` to store raw CSV files.
2. **Create IAM Roles and Policies**
    * To ensure proper permission, let's create an IAM Role for Lambda and Glue.
      - **Lambda-S3-Glue-Role**: Create an IAM Role to be assumed by the Lambda function, and attach the `AmazonS3FullAccess` and the `AWSGlueServiceRole` policies.
      - **Glue-Service-Role**: Create an IAM Role to be assumed by the Glue job, and attach the `AmazonS3FullAccess` and the `AWSGlueServiceRole` policies.
3. **Set up the Amazon QuickSight account**
   * If we are using Amazon QuickSight for the first time, the console will ask us to create a QuickSight account.
     - Select the authentication method as **QuickSight managed users and IAM Federated identity**. 
     - Next, configure QuickSight settings. 
  We need to allow access and auto discovery for some of the resources.
        - Click on the user icon > Manage Quick Sight > Under 'Shortcuts' click on 'AWS resources' > Select 'Amazon S3' > Select all three S3 buckets that we created earlier > Save.

### Step 2: Data ingestion and pre-processing
1. **Create a Lambda function**
   * AWS Lambda helps us execute code in response to events without managing servers.
Create a Lambda function that triggers automatically when a file is added to the *csv-raw-data* S3 bucket. 
This function will clean and transform the data before saving it back to the *csv-processed-data* S3 bucket. 
     - While creating the Lambda function, select the runtime as Python 3.14, select the Role to be assumed by Lambda as **Lambda-S3-Glue-Role**, which was created earlier.

2. **Write the Lambda function code**
    * Lambda function code:
        - The code is written to automatically process CSV files uploaded to an S3 bucket(*csv-raw-data*). The function gets automatically triggered when there's an event in *csv-raw-data* bucket. It fetches the CSV files & reads its contents.
        - The function will also clean the data. It removes rows that contain missing values, keeping only complete rows. And then it creates a new CSV file, where it writes the clean data into a new CSV file in memory.
        - It uploads the processed file or clean file, into a different S3 bucket, i.e. *csv-processed-data*.
        - Once the code is added, click on `deploy` and the function will get updated.

3. **Set-up S3 Event trigger for Lambda**
    * We need to configure the *csv-raw-data* bucket to automatically trigger the Lambda function whenever a new file is uploaded to the bucket. 
    * In the Lambda function console, click on `+ Add trigger`> Source as 'S3' > Select the bucket as *csv-raw-data* > Select the 'Event types' as `All objects create events` and `PUT` > In 'Prefix', enter `raw/` > In 'Suffix', enter `.csv` > Acknowledge the **Recursive Invocation** and click on `Add`.

4. **Test the data ingestion and pre-processing part**
    * Upload any .csv files to the `raw/` folder in the *csv-raw-data* bucket. The Lambda function gets triggered, processes the .csv file and uploads it to the *csv-processed-data* bucket under `processed/` folder. 
      - With this test, we can confirm that the data ingestion and pre-processing is already automated. We can proceed to the next stage, where we'll set-up data transformation with **AWS Glue**.
      - **Troubleshooting** : If the *csv-processed-data* bucket is not filled with processed CSV files, We can check the errors under **monitor** section of the Lambda function. Click on `View CloudWatch logs`, it will take us to the CloudWatch page where we can analyze the issue.

### Step 3: Data transformation using AWS-Glue
1. **Set up an AWS Glue Data Catalog**
    * **AWS Glue** is a fully managed ETL, that helps transform and move data between different storage layers. In this step, we'll set up a Glue Job, define a Data Catalog & execute transformation on pre-processed CSV files stored in the S3 bucket.

    * **AWS Glue Data Catalog** is a centralized metadata repository that stores information about data sets making them easily searchable and accessible for analytics.

      * **Create Glue Catalog**:
        - Create a Database: A database serves as a logical container to organize the tables and metadata.
            - AWS Glue > Data Catalog > Databases > Add Database > Give a name `csv_data_pipeline_catalog` > Create database.

2. **Create a Crawler to discover data schema**
    * Create a crawler to discover data schema. Crawler automatically scans the data and creates metadata tables.
      - AWS Glue > Data Catalog > Crawlers > Create Crawler > Give a name `ProcessedCSVDataCrawler` > Add the Data Source by choosing the *csv-processed-data* bucket > Under 'Subsequent crawler runs', select 'Crawl all sub-folders' > Click 'Add an S3 data Source' > Select an IAM Role > Select the **Glue-Service-Role**, which was previously created > Under 'Output configuration', select the `csv_data_pipeline_catalog` as the Target database > Create crawler

    * **Run the Crawler**
      - Once the crawler is created, click on 'Run crawler'. Once the crawler completes running, a new table schema will be available in the Glue Data Catalog. This can be verified under 'Data Catalog' > Databases > Tables 

3. **Create and Configure an AWS Glue Job using visual ETL**
    * Lets create a visual ETL pipeline using 'Visual ETL'. This is how we can visually represent or create a Glue Job.
      * **Add the Glue Job layer**: This is the first layer, which is the data source layer.
        - AWS Glue > ETL jobs > Visual ETL > Under 'Visual' tab, Under 'Sources' add 'AWS Glue Data Catalog' > Click on the 'AWS Glue Data Catalog' preview > Choose the Database as `csv_data_pipeline_catalog` > Select the table created by Glue Crawler > Select the IAM role as 'Glue-Service-Role' > Provide a name for the Job such as 'CSVDataTransformation' in the Top-left corner of the screen > Click on 'Save'
      * **Add the transform layer**: This layer transforms the data.
        - Click on 'Add(+)' > Under 'Transforms' > Select 'Change Schema' for basic transformation > This automatically takes the node parent as 'AWS Glue Data Catalog' > We can transform the data by unclicking any 'Source key'. For example, unselect 'icon' key to ignore it from the data > Click on 'Save'
      * **Add the target layer**: Placing the transformed data into the final S3 bucket.
        - Click on 'Add(+)' > Under 'Targets' > Select 'Amazon S3' > select the 'format' as 'CSV' > Change the 'compression type' to 'GZIP' > Select the target location as *csv-final-data* S3 bucket > Click on 'Save'

    * After creating all the layers, go ahead and 'Run' the Glue Job. Once the Job is executed, it will the transformed file into the *csv-final-data* S3 bucket.
      - Go to the *csv-final-data* S3 bucket to verify the new file. Download the `.gz` file to the local machine, rename it with `.csv` extension to view it. 

4. **Verify and Prepare transformed data for Visualization**
   * Since `.gz` files are not supported in Amazon QuickSight. 
Upload the file renamed with `.csv` extension to the *csv-final-data* S3 bucket, so that we can visualize the data using QuickSight.

### Step 4: Data Visualization with Amazon QuickSight
  * In the previous steps we have successfully automated the ingestion & transformation of CSV data using S3, Lambda and Glue. In this final step, we will visualize this processed data using Amazon QuickSight, which will help turn processed data into actionable insights.

    1. **Connect the data source**
       * Connect QuickSight to the processed data in the S3.
         * Go to Amazon QuickSight > In the left side panel, Click on 'DataSets' > Create dataset > Create data source > Select 'S3' > Give the data source name as 'ProcessedCSV' and Upload a manifest file. A manifest file is a JSON file is required in order to work with QuickSight. In the 'URIs' of the manifest file, add the URI of the final data/file present in the S3 bucket, that we want to analyze. > Then upload the manifest file > connect > Visualize

    2. **Build a QuickSight dashboard**
        * To visualize the data, select the 'Dataset' as 'ProcessedCSV' > Under 'Visuals', Select 'Vertical Stacked bar chart' > Select 'timestamp_local' for X AXIS > Select 'clouds_hi(Count) for 'Value'.
          - Once the Data is ready, the dashboard will be ready to view.

## Glossary
The difference between **pre-processing through Lambda** and **Glue ETL**:
| **pre-processing through Lambda** | **Glue ETL** |
|----------------------------------|-------------|
| Lambda is ideal for real-time processing lightweight or small files | Suited for large scale complex transformation on big data with built in schema discovery & job orchestration |

## References
1. [What is AWS Glue?](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
2. [Amazon Quick Sight](https://docs.aws.amazon.com/quicksight/latest/developerguide/welcome.html)
<!--
title: 'AWS Simple HTTP Endpoint example in Python'
description: 'This template demonstrates how to make a simple HTTP API with Python running on AWS Lambda and API Gateway using the Serverless Framework.'
layout: Doc
framework: v4
platform: AWS
language: python
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, Inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->

# OpenVPN-bot on AWS (Serverless) - In Progress

Why I make this? Well, I hate to pay a services when I didn't use it frequently but I still want a secured connection sometimes in public. I felt it was such a waste when  subscribed to a VPN service for $10/month or $4/month (with annual plan) but only use it once a week and not more than 2 hours per usage.

Thank lord now I'm  in a cloud era and able to write these set of scripts consists of Serverless, AWS Lambda (Python), AWS Cloudformation, Telegram bot API and Shell script. Feel free to give a try and give some comment if got any. Cheers!

## 📝Requirement

I'm sorry if this project was complicated. A lot of tools were used and need to setup before proceeding to **Usage** section. But please bare with me, I will try to explain the setup as much details as possible.
1. AWS account (verified):
   - **AWS cli** - latest version. Refer here for the [manual](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) of installation.
   - **IAM user** - admin privilege. Create the user with NoConsoleLogin but only programmatic access (Access key & Secret Key). Save the details to configure the AWS cli. 
   - Find your terminal and start configure the credentials using command `aws configure` and insert the access key and secret key once prompted.
   - **SES credentials** - verified identities.
2. Serverless:
   - We will mainly using serverless to develop and deploy the code into the AWS environment
3. Telegram Bot:
   - Basically you need to have a bot and a token to interact with it.
   - Refer to this [manual](www.google.com) to create a new bot and generate new token
4. Python:
   - This project were developed using Python **3.12** so you must have a Python with minimum version of 3.0.
   - **pip** installer - Python with version 3.4+ should already have it but if not, try to refer in [here](https://stackoverflow.com/a/6587528/13464580)
   - **venv** - It is practical to have isolated python environment when developing the project. If you don't have it yet, refer to this [page](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).  
5. NodeJS:
   - This project were developed using NodeJS **10.0.1**.

## ⌛ Progress

I still couldn't believe that I have created this mess. A lot of changes I have made and a lot of things that need to do too. Maybe this project already been made by others with better structure and better solution. However, I'm proud with myself able to bring out this kind of project until now.

### 🎯 Goals

There's such many ways to improve in this project in terms of code quality, security, consistency and many more. But here is what I could think of in the moment:

  - This is nonsense! I need to create a local test environment first.
  - Integrate with SNS for cloudformation status
  - Organize code function
  - Generalize the deployment steps


### ✅ Completed

Since this is my personal project, the pace of development definitely will not be consistent. However, progress are still progress. It's not perfect but it is better than nothing. So this is milestone that I have reached.
  - Implement authentication, this need email and db service (DynamoDB, SES) - DONE 
  - Adding progress tracker in [README.md](README.md)


## 🏃Usage
I need to think of how to streamline the procedure to deploy and start using it with comprehensive manual. In the same time, I also want to let others customize the functions more easily with a clear explanation.


### Deployment

```
serverless deploy
```

After deploying, you should see output similar to:

```
Deploying "aws-python-http-api" to stage "dev" (us-east-1)

✔ Service deployed to stack aws-python-http-api-dev (85s)

endpoint: GET - https://6ewcye3q4d.execute-api.us-east-1.amazonaws.com/
functions:
  hello: aws-python-http-api-dev-hello (2.3 kB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can call the created application via HTTP:

```
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/
```

Which should result in response similar to the following (removed `input` content for brevity):

```json
{
  "message": "Go Serverless v4.0! Your function executed successfully!"
}
```

### Local development

You can invoke your function locally by using the following command:

```
serverless invoke local --function hello
```

Which should result in response similar to the following:

```json
{
  "statusCode": 200,
  "body": "{\n  \"message\": \"Go Serverless v4.0! Your function executed successfully!\"}"
}
```

Alternatively, it is also possible to emulate API Gateway and Lambda locally by using `serverless-offline` plugin. In order to do that, execute the following command:

```
serverless plugin install -n serverless-offline
```

It will add the `serverless-offline` plugin to `devDependencies` in `package.json` file as well as will add it to `plugins` in `serverless.yml`.

After installation, you can start local emulation with:

```
serverless offline
```

To learn more about the capabilities of `serverless-offline`, please refer to its [GitHub repository](https://github.com/dherault/serverless-offline).

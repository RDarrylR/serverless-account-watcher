# Serverless AWS Account Watcher

### Purpose
Example SAM project to monitor AWS account related events and notifying interested parties using SNS and Slack when key changes occur.

### Key Files

- `account_event_handler` - Source for the AWS Lambda function
- `samconfig.toml` - Project configuration file.
- `template.yaml` - A template that defines the application's AWS resources.

### Requirements

-   [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) (NOTE the latest version may be needed if you see errors about "LoggingConfig" or other items)
-   Python 3.12 available to the sam cli. You will get errors about Python 3.12 not being found if you don't have it

### Deploy the sample project

To deploy the project, you need the following tools:

```bash
 sam build
 sam deploy
```

### Cleanup

To delete the sample project please use the AWS CLI or Console and delete the Cloudformation stack SAM created. You can also use the SAM CLI as below but please ensure all the resoures are actually gone in the AWS CLI/Console to ensure you have no ongoing AWS charges

```bash
sam delete
```

### Read More

This repository is associated with the following blog [posted here](https://darryl-ruggles.cloud/)
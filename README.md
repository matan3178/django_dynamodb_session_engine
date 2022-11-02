# Django DynamoDB Sessions Engine 

After a deep search of a way to get rid of relational database for a modern Django app's sessions, I decided to
implement it by myself

Follow the instructions below to set up your DynamoDB sessions 

Enjoy!

## Prepare you DynamoDB

#### 1. Create the table

Create the sessions table

##### Local Machine

    aws dynamodb create-table --table-name SESSIONS_TABLE_NAME --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --billing-mode PAY_PER_REQUEST  --endpoint-url http://localhost:8000

##### Remote (AWS)

    aws dynamodb create-table --table-name SESSIONS_TABLE_NAME --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --billing-mode PAY_PER_REQUEST

Note: Change the `billing-mode` to whatever fits your needs, and replace the `SESSIONS_TABLE_NAME` with your table name.

#### 2. Enable TTL in the new table

This will handle the auto-deletion of the sessions after the expiration date

##### Local Machine

    aws dynamodb update-time-to-live --table-name SESSIONS_TABLE_NAME --time-to-live-specification "Enabled=true, AttributeName=TTL_ATTR_NAME" --endpoint-url http://localhost:8000

##### Remote (AWS)

    aws dynamodb update-time-to-live --table-name SESSIONS_TABLE_NAME --time-to-live-specification "Enabled=true, AttributeName=TTL_ATTR_NAME"

Note: Replace the `SESSIONS_TABLE_NAME` and the `TTL_ATTR_NAME` with the appropriate values.

## Set your environment

1. Add `django.contrib.sessions` to your `INSTALLED_APPS` in `settings.py`
2. Add `django.contrib.sessions.middleware.SessionMiddleware` to your `MIDDLEWARE` in `settings.py`
3. Copy the `dynamodb_session.py` to your application
4. Add the `SESSION_ENGINE` field to your `settings.py` file. It's value should be the path to the `dynamodb_session.py`
   file
5. Add the following settings to your `settings.py` file:
    * `DYNAMODB_LOCAL_ENDPOINT` - A url points to your local DynamoDB instance
    * `DYNAMODB_REGION` - The region of your production dynamodb instance in AWS
    * `DYNAMODB_SESSIONS_TABLE` - The table name to be used as the Django sessions table
    * `DYNAMODB_SESSIONS_ATTR_ID` - The name of the session ID attribute in the table
    * `DYNAMODB_SESSIONS_ATTR_TTL` - The name of the ttl (expiration date) attribute in the table
    * `DYNAMODB_SESSIONS_ATTR_SESSION_DATA` - The name of the session's data attribute in the table

#### There is an example settings file (`settings_example.py`) in the repo that you can use as a reference

## Enjoy!
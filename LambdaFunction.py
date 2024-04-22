import json
import boto3
import time
import random
from datetime import datetime
from decimal import Decimal
import uuid

#pipeline worked!

# Initialize DynamoDB client for Transaction table
dynamodb_transaction = boto3.resource('dynamodb')
transaction_table_name = 'TransactionTable'
transaction_table = dynamodb_transaction.Table(transaction_table_name)

# Initialize DynamoDB client for Merchant table
dynamodb_merchant = boto3.resource('dynamodb')
merchant_table_name = 'Merchant'
merchant_table = dynamodb_merchant.Table(merchant_table_name)

# Initialize DynamoDB client for Bank table
dynamodb_bank = boto3.resource('dynamodb')
bank_table_name = 'Bank'
bank_table = dynamodb_bank.Table(bank_table_name)

def lambda_handler(event, context):
    print(event)

    # Parse the request body JSON data
    if 'body' in event and event['body']:
        body = json.loads(event['body'])
        if 'merchant_name' in body and 'merchant_token' in body:
            merchant_name = body['merchant_name']
            merchant_token = body['merchant_token']
            
            # Query Merchant DynamoDB table to check if MerchantName and Token exist
            merchant_response = merchant_table.get_item(
                Key={
                    'MerchantName': merchant_name,
                    'Token': merchant_token
                }
            )
            
            # Check if the item exists in Merchant DynamoDB table
            if 'Item' in merchant_response:
                # Query Bank DynamoDB table to check if account exists and balance is sufficient
                bank = body.get('bank')
                cc_number = body.get('cc_num')  # Keep original cc_number
                card_type = body.get('card_type')
                amount = Decimal(str(body.get('amount')))  # Convert to Decimal
                
                if amount <= Decimal('0.0'):
                    return {
                        "statusCode": 401,
                        "body": json.dumps({"message": "Non-positive number"})
                    }
                
                if card_type == 'Credit':
                    max_retries = 5
                    retry_delay = 1
                    
                    for attempt in range(max_retries):
                        try:
                            bank_response = bank_table.get_item(
                                Key={
                                    'BankName': bank,
                                    'CCNumber': int(cc_number)
                                }
                            )
                            
                            if random.randint(0, 6) == 5:
                                response_message = "Bank server error, retrying soon..."
                                temp_cc_number = str(cc_number)[-4:]
                                transaction_id = str(uuid.uuid4())  # Generate a unique identifier for the transaction
                                transaction_data = {
                                    'MerchantId': merchant_name,
                                    'TransactionId': transaction_id,
                                    'CardNumber': int(temp_cc_number),  # Convert to integer
                                    'Token': merchant_token,
                                    'Amount': amount,
                                    'Date': datetime.now().isoformat(),
                                    'ResponseMessage': response_message
                                }
                                transaction_table.put_item(Item=transaction_data)
                                time.sleep(retry_delay)  # Add a delay before retrying
                                retry_delay *= 2  # Exponential backoff for retry delay
                                continue  # Retry the code
                                
                            # Bank operation succeeded, break out of the retry loop
                            break
                    
                        except Exception as e:
                            print("Error:", e)
                            time.sleep(retry_delay)  # Add a delay before retrying
                            retry_delay *= 2  # Exponential backoff for retry delay
                    
                    # Check if the bank response is available after retries
                    if 'Item' in bank_response:
                        # Process the bank response
                        account_balance = Decimal(str(bank_response['Item'].get('CreditLimit', '0'))) - Decimal(str(bank_response['Item'].get('CreditUsed', '0')))
                        if account_balance >= amount:
                            response_message = "Approved"
                        else:
                            response_message = "Insufficient funds"
                    else:
                        response_message = "Account not found"
                elif card_type == 'Debit':
                    max_retries = 5
                    retry_delay = 1
                    
                    for attempt in range(max_retries):
                        try:
                            bank_response = bank_table.get_item(
                                Key={
                                    'BankName': bank,
                                    'CCNumber': int(cc_number)
                                }
                            )
                            
                            if random.randint(0, 6) == 5:
                                response_message = "Bank server error, trying again soon..."
                                temp_cc_number = str(cc_number)[-4:]
                                transaction_id = str(uuid.uuid4())  # Generate a unique identifier for the transaction
                                transaction_data = {
                                    'MerchantId': merchant_name,
                                    'TransactionId': transaction_id,
                                    'CardNumber': int(temp_cc_number),  # Convert to integer
                                    'Token': merchant_token,
                                    'Amount': amount,
                                    'Date': datetime.now().isoformat(),
                                    'ResponseMessage': response_message
                                }
                                transaction_table.put_item(Item=transaction_data)
                                time.sleep(retry_delay)  # Add a delay before retrying
                                retry_delay *= 2  # Exponential backoff for retry delay
                                continue  # Retry the code
                                
                            # Bank operation succeeded, break out of the retry loop
                            break
                    
                        except Exception as e:
                            print("Error:", e)
                            time.sleep(retry_delay)  # Add a delay before retrying
                            retry_delay *= 2  # Exponential backoff for retry delay
                    
                    # Check if the bank response is available after retries
                    if 'Item' in bank_response:
                        # Process the bank response
                        account_balance = Decimal(str(bank_response['Item'].get('Balance', '0')))
                        if account_balance >= amount:
                            response_message = "Approved"
                        else:
                            response_message = "Insufficient funds"
                    else:
                        response_message = "Account not found"
            else:
                response_message = "Merchant not Authorized"
                cc_number = 0000  # Set CardNumber to '0000' if merchant is not authorized
                amount = 0
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "MerchantName and MerchantToken are required in the request body"})
            }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Request body is missing"})
        }

    # Record transaction to Transaction DynamoDB table
    # Convert cc_number to last 4 digits before saving to the transaction table
    cc_number = str(cc_number)[-4:]
    transaction_id = str(uuid.uuid4())

    transaction_data = {
        'MerchantId': merchant_name,
        'TransactionId': transaction_id,
        'CardNumber': int(cc_number),  # Convert to integer
        'Token': merchant_token,
        'Amount': amount,
        'Date': datetime.now().isoformat(),
        'ResponseMessage': response_message
    }
    transaction_table.put_item(Item=transaction_data)

    return {
        "statusCode": 200 if response_message == "Approved" else 401,
        "body": json.dumps({"message": response_message})
    }

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
books_table = dynamodb.Table('books')
movies_table = dynamodb.Table('movies')

def put_book(item: dict):
    books_table.put_item(Item=item)
    
def get_all_books():
    return books_table.scan()

def get_book(id: str):
    return books_table.get_item(Key={'id': id})
    
def update_book(id: str, updates: dict):
    updates_expr = build_update_expression(updates)

    books_table.update_item(
        Key={'id': id},
        UpdateExpression=updates_expr['UpdateExpression'],
        ExpressionAttributeNames=updates_expr['ExpressionAttributeNames'],
        ExpressionAttributeValues=updates_expr['ExpressionAttributeValues']
    )
    
def delete_book(id: str):
    books_table.delete_item(Key={'id': id})

def put_movie(item: dict):
    movies_table.put_item(Item=item)
    
def get_all_movies():
    return movies_table.scan()

def get_movie(id: str):
    return movies_table.get_item(Key={'id': id})
    
def update_movie(id: str, updates: dict):
    updates_expr = build_update_expression(updates)

    movies_table.update_item(
        Key={'id': id},
        UpdateExpression=updates_expr['UpdateExpression'],
        ExpressionAttributeNames=updates_expr['ExpressionAttributeNames'],
        ExpressionAttributeValues=updates_expr['ExpressionAttributeValues']
    )
    
def delete_movie(id: str):
    movies_table.delete_item(Key={'id': id})

def build_update_expression(updates: dict) -> dict:
    """
    Takes a dict of attribute updates and returns the three arguments
    needed for update_item.

    Usage:
        args = build_update_expression({'age': 31, 'status': 'active'})
        table.update_item(Key={...}, **args)
    """

    set_expressions = []
    remove_expressions = []
    attr_names = {}
    attr_values = {}

    for key, value in updates.items():
        safe_key = f'#k_{key}'
        attr_names[safe_key] = key

        if value is None:
            remove_expressions.append(safe_key)
        else:
            placeholder = f':v_{key}'
            set_expressions.append(f'{safe_key} = {placeholder}')
            attr_values[placeholder] = value
    
    expression_parts = []
    if set_expressions:
        expression_parts.append('SET ' + ', '.join(set_expressions))
    if remove_expressions:
        expression_parts.append('REMOVE ' + ', '.join(remove_expressions))
    
    return {
        'UpdateExpression': ' '.join(expression_parts),
        'ExpressionAttributeNames': attr_names,
        'ExpressionAttributeValues': attr_values if attr_values else None
    }     
output "fastapi_server_public_ip" {
    value = aws_instance.fastapi_server.public_ip
    description = "Public IP to SSH into the instance"
}

output "fastapi_server_arn" {
    value = aws_instance.fastapi_server.arn
    description = "ARN of FastAPI server"
}

output "dynamodb_books_table_arn" {
    value = aws_dynamodb_table.books_table.arn
    description = "ARN of Books Table"
}

output "dynamodb_movies_tables_arn" {
    value = aws_dynamodb_table.movies_table.arn
    description = "ARN of Movies Table"
}
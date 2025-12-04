# Product Overview

A serverless REST API for managing events with full CRUD operations. Built for scalability and cost-efficiency using AWS serverless architecture.

## Core Features

- Event management with custom IDs, status tracking, and filtering
- Input validation with Pydantic models
- CORS-enabled for web access
- Comprehensive error handling
- OpenAPI/Swagger documentation

## Event Properties

Events include: eventId, title, description, date, location, capacity, organizer, and status (active, scheduled, ongoing, completed, cancelled).

## Architecture

- FastAPI backend running on AWS Lambda (ARM64)
- API Gateway for HTTPS endpoints
- DynamoDB for serverless data storage
- Docker-based Lambda deployment
- AWS CDK for infrastructure as code

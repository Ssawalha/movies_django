# Amman Movies API Documentation

## Overview

The Amman Movies API provides endpoints for accessing movie showings across different cinemas in Jordan. The API allows you to:

- Get active movie showings
- Retrieve movie information
- Access cinema locations
- Manage showing batches

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

Currently, the API is open and doesn't require authentication. Future versions will implement JWT authentication.

## Endpoints

### Movies

#### List All Movies

```http
GET /movies/
```

Returns a list of all movies across different cinemas.

**Response**

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/movies/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Movie Title",
      "normalized_title": "movie title",
      "grand_id": "123",
      "prime_id": "456",
      "taj_id": "789",
      "created_at": "2024-03-21T12:00:00Z",
      "updated_at": "2024-03-21T12:00:00Z"
    }
  ]
}
```

#### Get Movie Details

```http
GET /movies/{id}/
```

Returns detailed information about a specific movie.

**Response**

```json
{
  "id": 1,
  "title": "Movie Title",
  "normalized_title": "movie title",
  "grand_id": "123",
  "prime_id": "456",
  "taj_id": "789",
  "showings": [
    {
      "id": 1,
      "location": {
        "id": 1,
        "name": "Cinema Name",
        "city": "Amman",
        "address": "Address"
      },
      "date": "2024-03-22",
      "time": "19:00:00",
      "is_showing": true
    }
  ],
  "created_at": "2024-03-21T12:00:00Z",
  "updated_at": "2024-03-21T12:00:00Z"
}
```

### Showings

#### List Active Showings

```http
GET /showings/active/
```

Returns a list of currently active movie showings.

**Response**

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/showings/active/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "movie": {
        "id": 1,
        "title": "Movie Title"
      },
      "location": {
        "id": 1,
        "name": "Cinema Name",
        "city": "Amman"
      },
      "date": "2024-03-22",
      "time": "19:00:00",
      "is_showing": true
    }
  ]
}
```

#### Get Showing Details

```http
GET /showings/{id}/
```

Returns detailed information about a specific showing.

**Response**

```json
{
  "id": 1,
  "movie": {
    "id": 1,
    "title": "Movie Title",
    "normalized_title": "movie title"
  },
  "location": {
    "id": 1,
    "name": "Cinema Name",
    "city": "Amman",
    "address": "Address",
    "website": "https://example.com"
  },
  "date": "2024-03-22",
  "time": "19:00:00",
  "is_showing": true,
  "url": "https://example.com/booking",
  "created_at": "2024-03-21T12:00:00Z",
  "updated_at": "2024-03-21T12:00:00Z"
}
```

### Locations

#### List All Locations

```http
GET /locations/
```

Returns a list of all cinema locations.

**Response**

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Cinema Name",
      "city": "Amman",
      "address": "Address",
      "website": "https://example.com",
      "showings_count": 5
    }
  ]
}
```

#### Get Location Details

```http
GET /locations/{id}/
```

Returns detailed information about a specific location.

**Response**

```json
{
  "id": 1,
  "name": "Cinema Name",
  "city": "Amman",
  "address": "Address",
  "website": "https://example.com",
  "showings": [
    {
      "id": 1,
      "movie": {
        "id": 1,
        "title": "Movie Title"
      },
      "date": "2024-03-22",
      "time": "19:00:00",
      "is_showing": true
    }
  ],
  "created_at": "2024-03-21T12:00:00Z",
  "updated_at": "2024-03-21T12:00:00Z"
}
```

### Batches

#### List All Batches

```http
GET /batches/
```

Returns a list of all processing batches.

**Response**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "batch_id": "batch_123",
      "status": "COMPLETED",
      "created_at": "2024-03-21T12:00:00Z",
      "updated_at": "2024-03-21T12:00:00Z"
    }
  ]
}
```

#### Get Batch Details

```http
GET /batches/{id}/
```

Returns detailed information about a specific batch.

**Response**

```json
{
  "id": 1,
  "batch_id": "batch_123",
  "status": "COMPLETED",
  "showings": [
    {
      "id": 1,
      "movie": {
        "id": 1,
        "title": "Movie Title"
      },
      "location": {
        "id": 1,
        "name": "Cinema Name"
      },
      "date": "2024-03-22",
      "time": "19:00:00",
      "is_showing": true
    }
  ],
  "movies": [
    {
      "id": 1,
      "title": "Movie Title",
      "normalized_title": "movie title"
    }
  ],
  "created_at": "2024-03-21T12:00:00Z",
  "updated_at": "2024-03-21T12:00:00Z"
}
```

## Error Responses

The API uses standard HTTP response codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": ["Error message for specific field"]
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Limits are:

- 100 requests per minute per IP address
- 1000 requests per hour per IP address

## Versioning

The API is versioned through the URL path. Current version is v1.

## Support

For support or questions, please open an issue in the project repository.

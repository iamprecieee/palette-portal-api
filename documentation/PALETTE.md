# Genre
## GenreListView
- <i><b>Endpoint</b></i>: `/api/v1/palette/genre/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Retrieves an existing cached list of all existing genres. If none exists, retrieves an caches a non-cached list; does not require authentication. 

### Request Example (No content):
```shell
GET /api/v1/palette/genre/ HTTP/1.1
Host: 127.0.0.1
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
        "name": "Abstract",
        "slug": "abstract",
        "created": "2024-07-17T12:36:54.235846Z"
    },
    {
        "id": "65e1358d-69cb-4cf4-8d03-8c4ff1caee99",
        "name": "Cubism",
        "slug": "cubism",
        "created": "2024-07-17T12:38:02.482388Z"
    }
]
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Creates a new genre object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes; restricted to admins.

### Request Example:
```shell
POST /api/v1/palette/genre/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "name": "Abstract"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Abstract",
    "slug": "abstract",
    "created": "2024-07-17T12:36:54.235846Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Name field cannot be blank."
}
```
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Genre with this name already exists."
}
```
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be an admin to perform this action."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## GenreDetailView
- <i><b>Endpoint</b></i>: `/api/v1/palette/genre/<slug:slug>/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Retrieves an existing cached genre object. If none exists, retrieves an caches an non-cached object; uses both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /api/v1/palette/genre/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Abstract",
    "slug": "abstract",
    "created": "2024-07-17T12:36:54.235846Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Genre does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: PUT
- <i><b>Description</b></i>: Updates an existing genre object (and related cache) using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes; also updates the cache for both genre list and corresponding genre object. User must be an admin, or will be denied permission.

### Request Example:
```shell
PUT /api/v1/palette/genre/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "name": "Renaissance"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 202 Accepted
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Renaissance",
    "slug": "renaissance",
    "created": "2024-07-17T12:36:54.235846Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Update error. You can only update the Name field. Slug field updates automatically."
}
```
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be an admin to perform this action."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Genre does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

- <i><b>Method</b></i>: DELETE
- <i><b>Description</b></i>: Deletes an existing genre object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be an admin, or will be denied permission. Cache is updated to reflect changes.

### Request Example (No content):
```shell
DELETE /api/v1/palette/genre/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 204 No Content
Content-Type: application/json
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be an admin to perform this action."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Genre does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

# Artwork
## ArtworkListView
- <i><b>Endpoint</b></i>: `/api/v1/palette/artwork/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Retrieves an existing cached list of all existing artworks. If none exists, retrieves an caches a non-cached list; does not require authentication. 

### Request Example (No content):
```shell
GET /api/v1/palette/genre/ HTTP/1.1
Host: 127.0.0.1
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
        "name": "Scream",
        "slug": "abstract",
        "description": "",
        "image": "",
        "artist": "admin",
        "height": "",
        "width": "",
        "price": "",
        "genre": ["Appropriation"],
        "is_available": "True", 
        "created": "2024-07-17T12:36:54.235846Z",
        "updated": "2024-07-17T16:23:53.710295Z"
    }
]
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Creates a new artwork object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes, and MultiPartParser as parser_class to handle JSON and binary data; restricted to artists. 
On artwork creation, the image is uploaded to cloudinary, and its url is stored in the db `image` field

### Request Example:
```shell
POST /api/v1/palette/artwork/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Scream",
    "slug": "abstract",
    "description": "",
    "image": "",
    "artist": "admin",
    "height": "",
    "width": "",
    "price": "",
    "genre": ["Appropriation"],
    "is_available": "True", 
    "created": "2024-07-17T12:36:54.235846Z",
    "updated": "2024-07-17T16:23:53.710295Z"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Abstract",
    "slug": "abstract",
    "created": "2024-07-17T12:36:54.235846Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

[
    "Genres field is required.",
    "Name field cannot be blank.",
    "Image field is required."
]
```
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Artwork with this name already exists."
}
```
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be an artist to perform this action."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## ArtworkDetailView
- <i><b>Endpoint</b></i>: `/api/v1/palette/artwork/<slug:slug>/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Retrieves an existing cached artwork object. If none exists, retrieves an caches an non-cached object; uses both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /api/v1/palette/artwork/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Scream",
    "slug": "abstract",
    "description": "",
    "image": "",
    "artist": "admin",
    "height": "",
    "width": "",
    "price": "",
    "genre": ["Appropriation"],
    "is_available": "True", 
    "created": "2024-07-17T12:36:54.235846Z",
    "updated": "2024-07-17T16:23:53.710295Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Artwork does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: PUT
- <i><b>Description</b></i>: Updates certain details (excluding name, artist, and image) of an existing artwork object (and related cache) using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be the artwork's creator, or will be denied permission.

### Request Example:
```shell
PUT /api/v1/palette/artwork/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "is_available": False
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 202 Accepted
Content-Type: application/json

{
    "id": "a3480186-e5db-44c0-aa34-de25530d42d2",
    "name": "Scream",
    "slug": "abstract",
    "description": "",
    "image": "",
    "artist": "admin",
    "height": "",
    "width": "",
    "price": "",
    "genre": ["Appropriation"],
    "is_available": "False", 
    "created": "2024-07-17T12:36:54.235846Z",
    "updated": "2024-07-17T16:23:53.710295Z"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Update error. You cannot edit the value of ['name'].."
}
```
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be the artwork's creator to perform this action."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Artwork does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

- <i><b>Method</b></i>: DELETE
- <i><b>Description</b></i>: Deletes an existing artwork object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be an admin, or will be denied permission. Cache is updated to reflect changes. The corresponding asset on cloudinary is also deleted.

### Request Example (No content):
```shell
DELETE /api/v1/palette/genre/<slug:slug>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 204 No Content
Content-Type: application/json
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be the artwork's creator to perform this action."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Artwork does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

# Cart
## CartListView
- <i><b>Endpoint</b></i>: `/api/v1/palette/cart/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Returns session cart data; requires user to be a collector and authenticated. 

### Request Example (No content):
```shell
GET /api/v1/palette/cart/ HTTP/1.1
Host: 127.0.0.1
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "detail": "You must be a collector to perform this action."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

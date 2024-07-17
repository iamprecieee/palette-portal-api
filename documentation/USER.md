# User Registration
## RegisterView
- <i><b>Endpoint</b></i>: `v1/user/register/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Registers a new user by accepting their registration data.

### Request Example:
```shell
POST /v1/user/register/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{
    "email": "admin@gmail.com",
    "username": "admin",
    "password": "Admin,123",
    "confirm_password": "Admin,123"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "72111ce4-8e06-47c7-8320-a3c0da6c550a",
    "email": "admin@gmail.com",
    "username": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "Password error. Password must contain at least 1 symbol."
}
```
```shell
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "User with this email already exists."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

# User Authentication
## KnoxLoginView
- <i><b>Endpoint</b></i>: `v1/user/login-knox/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Authenticates a user using [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [PaletteAuthToken](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L121) as its token model. This allows for multiple logged-in sessions by the same user (capped at 3).

### Request Example:
```shell
POST /v1/user/login-knox/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{
    "email": "admin@gmail.com",
    "password": "Admin,123"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "5ec090f4-2bfb-4e43-a1f0-2480d89aca03",
    "email": "admin@gmail.com",
    "username": "admin",
    "token": "ebb9c4f336b1d9f4697962d8a6b48c4f00d645ea1848f36d8236571cc1890584"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Authentication Failed
Content-Type: application/json

{
    "No active account found with the given credentials."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## JWTLoginView
- <i><b>Endpoint</b></i>: `v1/user/login-jwt/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Authenticates a user using SimpleJWT's [TokenObtainPairView](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/views.py#L51). This allows for stateless logins. On each login, the user's [SessionRefreshToken](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/refresh.py#L8) is updated to the current JWT refresh token and the previous one gets blacklisted.

### Request Example:
```shell
POST /v1/user/login-jwt/ HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{
    "email": "admin@gmail.com",
    "password": "Admin,123"
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMTI0NjY5NSwiaWF0IjoxNzIxMTYwMjk1LCJqdGkiOiJiNGEzNGVhNjgzZGU0MWViYTdiNTM1ODlkY2ExM2YxOSIsInVzZXJfaWQiOiJiMjg3NGYxOS05MDgyLTQ0ZjctOTc0MC00YmE4YzQ5MDVmMTUifQ.Uu5403H3Ac-S-52AdNiPVBCu-ZZbkgYl85iqcfHwWfQ",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMjg5ODk1LCJpYXQiOjE3MjExNjAyOTUsImp0aSI6ImQ3Njg1YTU4NDlhNzQxYjE5YTgxMTE4M2MzMDk3MjIzIiwidXNlcl9pZCI6ImIyODc0ZjE5LTkwODItNDRmNy05NzQwLTRiYThjNDkwNWYxNSJ9.tCR1YExRvVn-_vveq-zSbUecqee8FQhvYGAEoPoCWc4",
    "id": "b2874f19-9082-44f7-9740-4ba8c4905f15",
    "email": "admin@gmail.com",
    "username": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Authentication Failed
Content-Type: application/json

{
    "No active account found with the given credentials."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## JWTRefreshView
- <i><b>Endpoint</b></i>: `v1/user/token/refresh/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Returns a new token pair using the current JWT refesh token in the user's [SessionRefreshToken](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/refresh.py#L8) and updates the session data to the new pair.

### Request Example (No content):
```shell
POST /v1/user/token/refresh/ HTTP/1.1
Host: 127.0.0.1
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMjkxMDkwLCJpYXQiOjE3MjExNjE0OTAsImp0aSI6IjcwOGJlMDNkNDIxMTQ1Mjg5YTljNzIwNTk3MDk1ODVhIiwidXNlcl9pZCI6IjcwYTM2NTM0LTAzNGEtNDlmMi05MzY2LTM5YmE3N2VjZDhlYSJ9.r5cQTk9QYg5qo2jEUh4iq4KguCel-zb6v_ttTwo-gls",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMTI0Nzg5MCwiaWF0IjoxNzIxMTYxNDkwLCJqdGkiOiI4MjY1NjU0M2Q4M2Q0NjM5OTFhMGNmMjk4NDNjZWIyYiIsInVzZXJfaWQiOiI3MGEzNjUzNC0wMzRhLTQ5ZjItOTM2Ni0zOWJhNzdlY2Q4ZWEifQ.lulg7m7oKKP0bZxEeYnU77Wtf3fAnTYNNvL0bqpjz1w",
}
```
- <i><b>Error Response</b></i>:
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## KnoxLogoutView
- <i><b>Endpoint</b></i>: `v1/user/logout-knox/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Logs out the current user session using [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) as authentication_class. Any other knox sessions remain active.

### Request Example (No content):
```shell
POST /v1/user/logout-knox/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "User logged out successfully."
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Invalid token."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## JWTLogoutView
- <i><b>Endpoint</b></i>: `v1/user/logout-jwt/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Logs out the current user session using [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_class. The JWT access token is blacklisted using [JWTTokenBlacklist](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L173), and refresh token is removed from the session.

### Request Example (No content):
```shell
POST /v1/user/logout-jwt/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "User logged out successfully."
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Invalid token."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## KnoxLogoutAllView
- <i><b>Endpoint</b></i>: `v1/user/logout-knox-all/`
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Logs out all user sessions using [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) as authentication_class. Any other knox sessions tokens are deleted. This view inherits from knox's [LogoutAllView](https://github.com/jazzband/django-rest-knox/blob/develop/knox/views.py#L95).

### Request Example (No content):
```shell
POST /v1/user/logout-knox-all/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "Batch logout successful."
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Invalid token."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

# User Profile (Artist)
## ArtistProfileListView
- <i><b>Endpoint</b></i>: `v1/user/profile/artist/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Returns a list of all existing artists' data using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /v1/user/profile/artist/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "id": "764e3e7c-3c23-4f06-8a48-ef37abf3b8cf",
        "bio": "Making Art 1",
        "instagram": "https://instagram.com/admin1",
        "user": "admin1"
    },
    {
        "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
        "bio": "Making Art",
        "instagram": "https://instagram.com/admin",
        "user": "admin"
    }
]
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Creates a new artist object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example:
```shell
POST /v1/user/profile/artist/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "bio": "Just making art."
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just making art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 409 Conflict
Content-Type: application/json

{
    "This user has an existing artist profile."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## ArtistProfileDetailView
- <i><b>Endpoint</b></i>: `v1/user/profile/artist/<str:profile_id>/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Returns a dict of an existing artist's data using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /v1/user/profile/artist/<str:profile_id>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just making art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: PUT
- <i><b>Description</b></i>: Updates an existing artist object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be the profile owner, or will be denied permission.

### Request Example:
```shell
PUT /v1/user/profile/artist/<str:profile_id>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "bio": "Just making more art."
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 202 Accepted
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just making more art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "You are not allowed to operate on another user's profile."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

- <i><b>Method</b></i>: DELETE
- <i><b>Description</b></i>: Deletes an existing artist object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be the profile owner, or will be denied permission.

### Request Example (No content):
```shell
DELETE /v1/user/profile/artist/<str:profile_id>/ HTTP/1.1
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
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "You are not allowed to operate on another user's profile."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

# User Profile (Collector)
## CollectorProfileListView
- <i><b>Endpoint</b></i>: `v1/user/profile/collector/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Returns a list of all existing collectors' data using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /v1/user/profile/collector/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "id": "764e3e7c-3c23-4f06-8a48-ef37abf3b8cf",
        "bio": "Buying Art 1",
        "instagram": "https://instagram.com/admin1",
        "user": "admin1"
    },
    {
        "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
        "bio": "Buying Art",
        "instagram": "https://instagram.com/admin",
        "user": "admin"
    }
]
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: POST
- <i><b>Description</b></i>: Creates a new collector object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example:
```shell
POST /v1/user/profile/artist/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "bio": "Just buying art."
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just buying art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 409 Conflict
Content-Type: application/json

{
    "This user has an existing collector profile."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

## CollectorProfileDetailView
- <i><b>Endpoint</b></i>: `v1/user/profile/collector/<str:profile_id>/`
- <i><b>Method</b></i>: GET
- <i><b>Description</b></i>: Returns a dict of an existing collector's data using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes.

### Request Example (No content):
```shell
GET /v1/user/profile/collector/<str:profile_id>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Token 6edbb190af25503afcb1f84cb9754203e67a9318edef6705ce48ccea8c4b88c7
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just buying art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```
- <i><b>Method</b></i>: PUT
- <i><b>Description</b></i>: Updates an existing collector object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be the profile owner, or will be denied permission.

### Request Example:
```shell
PUT /v1/user/profile/collector/<str:profile_id>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM

{
    "bio": "Just buying more art."
}
```

### Response Examples:
- <i><b>Success Response</b></i>:
```shell
HTTP/1.1 202 Accepted
Content-Type: application/json

{
    "id": "034aefd8-1b01-4ea6-866a-8b37c148a759",
    "bio": "Just making buying art.",
    "instagram": "https://instagram.com/admin",
    "user": "admin"
}
```
- <i><b>Error Responses</b></i>:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "You are not allowed to operate on another user's profile."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```

- <i><b>Method</b></i>: DELETE
- <i><b>Description</b></i>: Deletes an existing collector object using both [PaletteTokenAuthentication](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L146) and [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) as authentication_classes. User must be the profile owner, or will be denied permission.

### Request Example (No content):
```shell
DELETE /v1/user/profile/collector/<str:profile_id>/ HTTP/1.1
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
    "Authentication credentials were not provided."
}
```
```shell
HTTP/1.1 403 Permission Denied
Content-Type: application/json

{
    "You are not allowed to operate on another user's profile."
}
```
```shell
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "Profile does not exist."
}
```
```shell
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "Request was throttled. Expected available in 60 seconds."
}
```


# [JWTBlacklistMiddleware](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/middleware.py#L8)
- <i><b>Description</b></i>: Intercepts requests to check if the provided JWT access token is blacklisted and returns an unauthorized response if the token is invalid. Works when [JWTAuthentication](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L27) is used as authentication_class.

## Middleware Behavior:
- <i><b>Token Extraction/Blacklist Check</b></i>: Extracts the token from the Authorization header, then checks if the token exists in the [JWTTokenBlacklist](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/models.py#L173) model.
- <i><b>Unauthorized Response</b></i>: If the token is blacklisted, returns a `401 Unauthorized` response with a message indicating the token is invalid.
- <i><b>JSON Rendering</b></i>: Uses `JSONRenderer` to render the response content as JSON.

## Example Usage:
### Request:
```shell
GET /v1/user/profile/collector/<str:profile_id>/ HTTP/1.1
Host: 127.0.0.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMzMxMjE5LCJpYXQiOjE3MjEyMDE2MTksImp0aSI6ImEzNDNmZDFmNjZlNTRkNGRiMjExMTcwNDM0NDI1YWE4IiwidXNlcl9pZCI6ImY2MWRkZjQ5LTc5NmUtNDExNi1iM2RmLTI5ZGE3ODFkNTgxYiJ9.WSjLHGEFXTxlaVvPEXASs-1vPeYoOnVZVoo13QheoNM
```
### Response:
- Token Blacklisted:
```shell
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "Invalid token."
}
```
- Token Valid:
Proceed to the requested endpoint if the token is not blacklisted.


# [SessionRefreshToken](https://github.com/iamprecieee/palette-portal-api/blob/b58a5a0127d0ff8c41678606a657a5ae8ac3dcae/user/refresh.py#L8)
- <i><b>Description</b></i>: Manages the storage, retrieval, and removal of refresh tokens in the user's session.
## Methods
```shell
__init__(self, request)
```
- <i><b>Description</b></i>: Initializes the session refresh token manager with the current request session. If no refresh token exists in the session, it initializes an empty dictionary to store it.

```shell
save(self)
```
- <i><b>Description</b></i>: Marks the session as modified to ensure the changes are saved.

```shell
add(self, refresh_token)
```
- <i><b>Description</b></i>: Adds a new refresh token to the session.
```shell
token(self)
```
- <i><b>Description</b></i>: Retrieves the current refresh token from the session.
- <i><b>Returns</b></i>: The refresh token stored in the session.
```shell
remove(self, modify=False)
```
- <i><b>Description</b></i>: Removes the refresh token from the session and optionally blacklists it if token rotation and blacklisting are enabled in settings.
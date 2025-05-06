
**Architecture Flow

[Client]
   |
   | HTTP Request with JWT Token in headers
   v
[Post Service (FastAPI)]
   |
   |--nginx--> [User Service]
   |         - Verifies JWT
   |         - Returns user_id, email, is_admin, etc.
   |
   | If valid, create post
   v
[PostgreSQL (post DB)]

**Reverse Proxy Instructions

1. **Nginx Setup**
   1. Go to the NGINX website and download the stable version for Windows.

   2. Extract the contents of the ZIP file to a folder (e.g., C:\nginx).

   3. Open the nginx.conf file located in the conf folder of your NGINX installation directory.

   4. Modify it as needed

2. **Run Nginx Inside Docker**

   Update your docker-compose.yml
   ```
   nginx:
      image: nginx:latest
      volumes:
        - ./nginx.conf:/etc/nginx/nginx.conf
      ports:
        - "8080:80"
      depends_on:
        - post_service
        - user_service
   ```

3. **nginx.conf file existance**
   
   1. Create nginx.conf  at the same dorectory level of the docker-compose file. File includes the updates we did in step 1(4)

   2. `docker compose up --build`

   3. **Test the service**
      http://localhost:8080/api/users or http://localhost:8080/api/posts


**********************************************gPRC Integration***********************************************
1. **Create proto directory at similar level of services**

2. **Create user.proto and post.proto files**

3. **Compile both .proto files to generate Python code for both services**
   ```
   python -m grpc_tools.protoc -I proto --python_out=user_service --grpc_python_out=user_service proto/user.proto
   python -m grpc_tools.protoc -I proto --python_out=post_service --grpc_python_out=post_service proto/user.proto proto/post.proto
   ```


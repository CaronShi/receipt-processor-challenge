Instructions

1. Open a terminal and navigate to the directory containing your Dockerfile, app.py, and requirements.txt.

2. Build the Docker image using the following command:
"docker build -t your-image-name ."

Replace your-image-name with a suitable name for your Docker image.

3. Once the image is built, you can run the Docker container using the following command:

"docker run -p 80:80 your-image-name"

Replace your-image-name with the name you used when building the image.

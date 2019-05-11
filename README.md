## gRPC Client-Server to compute Image-Similarity

A simple project demonstrating Client-Server model using gRPC

The clients selects 2 images, and sends them to server. The server computes
the similarity between those two images and sends the result back to client.
Server used ResNet to generate feature vector of the images and computes
cosine-similarity between feature vectors.


### Pre-Requisites
1. Python 3.6+
2. gRPC
3. Numpy
4. Python Pillow
5. Tkinter


### Compilation
```bash
virtualenv --system-site-packages -p python3 ./venv
source ./venv/bin/activate
git clone https://github.com/NamanRastogi/Image_Comparator.git
cd Image_Comparator
pip install -r requirements.txt
python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ ./commons/image_similarity.proto
```

### Run Server
```bash
python server/server.py
```

### Run Client
```bash
python client/client.py
```

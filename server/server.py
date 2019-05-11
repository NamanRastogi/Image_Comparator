"""Server.
"""

import logging
import time
import uuid

from concurrent import futures

import grpc
import numpy as np

from PIL import Image

from img_to_vec import Img2Vec
from commons import image_similarity_pb2
from commons import image_similarity_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ImageSimilarityServicerImpl(image_similarity_pb2_grpc.ImageSimilarityServicer):

    def __init__(self):
        self.logger = logging.getLogger("Server")
        self.logger.setLevel(logging.DEBUG)
        self.img2vec = Img2Vec()

    @staticmethod
    def compute_vec_similarity(vec_1, vec_2):
        return np.dot(vec_1, vec_2) / (np.linalg.norm(vec_1) * np.linalg.norm(vec_2))

    def compute_image_similarity(self, image_1, image_2):
        vec_1 = self.img2vec.get_vec(image_1, tensor=False)
        vec_2 = self.img2vec.get_vec(image_2, tensor=False)
        return self.compute_vec_similarity(vec_1, vec_2)

    def get_image_similarity(self, request, context):
        self.logger.info("Request received! Request ID: {}".format(request.request_id))
        resp_id = str(uuid.uuid4())
        image_1 = Image.frombytes(mode='RGB', size=(512, 512), data=request.image_1, decoder_name='raw')
        image_2 = Image.frombytes(mode='RGB', size=(512, 512), data=request.image_2, decoder_name='raw')
        similarity_val = self.compute_image_similarity(image_1, image_2)
        self.logger.info("Sending response! Response ID: {} Similarity: {}".format(resp_id, similarity_val))
        return image_similarity_pb2.Similarity(
            response_id=resp_id,
            similarity_val=similarity_val)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_similarity_pb2_grpc.add_ImageSimilarityServicer_to_server(ImageSimilarityServicerImpl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
    serve()
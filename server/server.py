#!/usr/bin/env python3

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

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(name)s : %(message)s')


class _ImageSimilarityServicerImpl(image_similarity_pb2_grpc.ImageSimilarityServicer):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
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
        self.logger.info(f'Request received! Request ID: {request.request_id}')
        resp_id = str(uuid.uuid4())
        image_1 = Image.frombytes(mode='RGB', size=(512, 512), data=request.image_1, decoder_name='raw')
        image_2 = Image.frombytes(mode='RGB', size=(512, 512), data=request.image_2, decoder_name='raw')
        similarity_val = self.compute_image_similarity(image_1, image_2)
        self.logger.info(f'Sending response! Response ID: {resp_id} Similarity: {similarity_val}')
        return image_similarity_pb2.Similarity(
            response_id=resp_id,
            similarity_val=similarity_val)


class Server:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        image_similarity_pb2_grpc.add_ImageSimilarityServicer_to_server(_ImageSimilarityServicerImpl(), self.server)

    def start(self, port):
        self.server.add_insecure_port(f'[::]:{port}')
        self.server.start()
        self.logger.info(f'Server started at port {port}')
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)
            self.logger.info('Server stopped!')


if __name__ == '__main__':
    server = Server()
    server.start(port='50051')

#!/usr/bin/env python3

import logging
import os
import uuid

import grpc
from PIL import Image
from tkinter import filedialog

from commons import image_similarity_pb2
from commons import image_similarity_pb2_grpc

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(name)s : %(message)s')


class Client:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def select_image(title='Select image'):
        return filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title=title,
            filetypes=(('JPEG files', '*.jpg'),
                       ('PNG file', '*.png')))

    @staticmethod
    def read_image(image_path):
        image_data = Image.open(image_path, 'r').resize((512, 512), Image.BICUBIC)
        return image_data.tobytes(encoder_name='raw')

    def query_server(self, ip, port):
        self.logger.info(f'Connecting {ip}:{port}')
        with grpc.insecure_channel(f'{ip}:{port}') as channel:
            stub = image_similarity_pb2_grpc.ImageSimilarityStub(channel)
            req_id = str(uuid.uuid4())
            image_1 = self.read_image(self.select_image('Select first image'))
            image_2 = self.read_image(self.select_image('Select second image'))
            self.logger.info(f'Requesting image similarity! Request ID: {req_id}')
            response = stub.get_image_similarity(image_similarity_pb2.Images(
                request_id=req_id,
                image_1=image_1,
                image_2=image_2))
            resp_id = response.response_id
            image_similarity_val = response.similarity_val
            self.logger.info(f'Response received! Response ID: {resp_id} Similarity: {image_similarity_val}')
            return image_similarity_val


if __name__ == '__main__':
    client = Client()
    val = client.query_server('localhost', '50051')
    print(f'Similarity: {val}')

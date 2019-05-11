import logging
import uuid

import grpc

from PIL import Image

from commons import image_similarity_pb2
from commons import image_similarity_pb2_grpc


def input_image(image_path):
    # logger
    image_data = Image.open(image_path, 'r').resize((512, 512), Image.BICUBIC)
    return image_data.tobytes(encoder_name='raw')


def run():
    logger = logging.getLogger("Client")
    logger.setLevel(logging.DEBUG)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = image_similarity_pb2_grpc.ImageSimilarityStub(channel)
        req_id = str(uuid.uuid4())
        image_1 = input_image("/home/naman/Documents/ImgComparator/client/im1.jpg")
        image_2 = input_image("/home/naman/Documents/ImgComparator/client/im2.jpg")
        logger.info("Requesting image similarity! Request ID: {}".format(req_id))
        response = stub.get_image_similarity(image_similarity_pb2.Images(
            request_id=req_id,
            image_1=image_1,
            image_2=image_2))
        resp_id = response.response_id
        image_similarity_val = response.similarity_val
        logger.info("Response received! Response ID: {} Similarity: {}".format(resp_id, image_similarity_val))
        print("Similarity: {}".format(image_similarity_val))


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
    run()

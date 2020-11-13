import logging
import recipes
import random

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

RECIPE_IMAGES = {
    'HON': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/honey mustard-sauce-500x500.png",
    'BBQ': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/barbecue-sauce-500x500.png",
    'THO': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/thousand island-sauce-500x500.png",
    'PES': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/pesto-sauce-500x500.png",
    'TAR': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/tartar-sauce-500x500.png",
    'PIZ': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/pizza-sauce-500x500.png",
    'CRA': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/cranberry-sauce-500x500.png",
    'SEC': "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/secret-sauce-500x500.png"
}

RECIPE_DEFAULT_IMAGE = "https://s3.amazonaws.com/ask-samples-resources/images/sauce-boss/secret-sauce-500x500.png"
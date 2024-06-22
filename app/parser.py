from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-p", "--port", help="8000 8001", type=int)
parser.add_argument("-e", "--environ", help="local dev prod", type=str)
args = parser.parse_args()

#!/bin/bash
# Proto 파일로부터 Python 코드 생성

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/library.proto

echo "Generated library_pb2.py and library_pb2_grpc.py"


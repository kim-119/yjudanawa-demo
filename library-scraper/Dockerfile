FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proto 파일 복사 및 코드 생성
COPY proto ./proto
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/library.proto

# 애플리케이션 코드 복사
COPY main.py .
COPY grpc_server.py .

# 포트 노출
EXPOSE 8090
EXPOSE 50051

# gRPC 서버 실행
CMD ["python", "grpc_server.py"]



package yju.danawa.com.service;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import yju.danawa.com.grpc.*;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

/**
 * gRPC 클라이언트를 통한 도서관 검색 서비스
 */
@Service
public class LibraryGrpcClient {

    private static final Logger log = LoggerFactory.getLogger(LibraryGrpcClient.class);

    private static final String GRPC_HOST = "library-scraper";
    private static final int GRPC_PORT = 50051;

    private ManagedChannel channel;
    private LibraryServiceGrpc.LibraryServiceBlockingStub blockingStub;

    @PostConstruct
    public void init() {
        // gRPC 채널 생성
        channel = ManagedChannelBuilder
                .forAddress(GRPC_HOST, GRPC_PORT)
                .usePlaintext() // TLS 없이 (개발 환경)
                .build();

        blockingStub = LibraryServiceGrpc.newBlockingStub(channel);

        log.info("gRPC 채널 생성: {}:{}", GRPC_HOST, GRPC_PORT);
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            channel.shutdown();
            log.info("gRPC 채널 종료");
        }
    }

    /**
     * 도서관 소장 여부 확인
     */
    public LibraryResponse checkLibrary(String isbn, String title) {
        try {
            LibraryRequest.Builder requestBuilder = LibraryRequest.newBuilder();

            if (isbn != null && !isbn.isBlank()) {
                requestBuilder.setIsbn(isbn);
            }
            if (title != null && !title.isBlank()) {
                requestBuilder.setTitle(title);
            }

            LibraryRequest request = requestBuilder.build();

            log.info("gRPC 호출: isbn={}, title={}", isbn, title);

            // gRPC 호출 (동기)
            LibraryResponse response = blockingStub.checkLibrary(request);

            log.info("gRPC 응답: found={}, available={}, location={}",
                    response.getFound(), response.getAvailable(), response.getLocation());

            return response;

        } catch (StatusRuntimeException e) {
            log.error("gRPC 호출 실패: {}", e.getStatus());
            throw new RuntimeException("gRPC 호출 실패", e);
        }
    }

    /**
     * 건강 체크
     */
    public HealthCheckResponse healthCheck() {
        try {
            HealthCheckRequest request = HealthCheckRequest.newBuilder().build();
            return blockingStub.healthCheck(request);
        } catch (StatusRuntimeException e) {
            log.error("gRPC 건강 체크 실패: {}", e.getStatus());
            throw new RuntimeException("gRPC 건강 체크 실패", e);
        }
    }
}


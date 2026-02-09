package yju.danawa.com.service;

import yju.danawa.com.dto.BookDto;
import yju.danawa.com.service.dto.AladinItemSearchResponse;
import yju.danawa.com.service.dto.KakaoBookResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ResponseStatusException;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class ExternalBookService {

    private final WebClient webClient;
    private final String kakaoRestApiKey;
    private final String aladinTtbKey;

    public ExternalBookService(WebClient.Builder builder,
                               @Value("${app.external.kakao-rest-api-key:}") String kakaoRestApiKey,
                               @Value("${app.external.aladin-ttb-key:}") String aladinTtbKey) {
        // 타임아웃 설정 추가
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofSeconds(10));

        this.webClient = builder
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
        this.kakaoRestApiKey = kakaoRestApiKey;
        this.aladinTtbKey = aladinTtbKey;
    }

    @Cacheable(cacheNames = "externalBooks", key = "#query + '::' + #source")
    public List<BookDto> search(String query, String source) {
        if (query == null || query.trim().isEmpty()) {
            return Collections.emptyList();
        }
        String normalizedSource = Optional.ofNullable(source).orElse("kakao").toLowerCase(Locale.ROOT);
        switch (normalizedSource) {
            case "aladin":
                return searchAladin(query);
            case "kakao":
                return searchKakao(query);
            case "auto":
                List<BookDto> kakaoResult = safeSearchKakao(query);
                return kakaoResult.isEmpty() ? safeSearchAladin(query) : kakaoResult;
            default:
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unsupported source: " + source);
        }
    }

    private List<BookDto> safeSearchKakao(String query) {
        try {
            return searchKakao(query);
        } catch (Exception ex) {
            return Collections.emptyList();
        }
    }

    private List<BookDto> safeSearchAladin(String query) {
        try {
            return searchAladin(query);
        } catch (Exception ex) {
            return Collections.emptyList();
        }
    }

    private List<BookDto> searchKakao(String query) {
        if (kakaoRestApiKey == null || kakaoRestApiKey.isBlank()) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Kakao API key not configured");
        }

        try {
            // 📚 페이징: 카카오는 최대 50권까지 (size 파라미터)
            KakaoBookResponse response = webClient.get()
                    .uri(uriBuilder -> uriBuilder
                            .scheme("https")
                            .host("dapi.kakao.com")
                            .path("/v3/search/book")
                            .queryParam("query", query)
                            .queryParam("size", 50)  // 🔥 하드코딩: 최대 50권
                            .build())
                    .header("Authorization", "KakaoAK " + kakaoRestApiKey)
                    .retrieve()
                    .onStatus(status -> status.is4xxClientError() || status.is5xxServerError(),
                            clientResponse -> {
                                throw new ResponseStatusException(
                                        HttpStatus.BAD_GATEWAY,
                                        "Kakao API 호출 실패: " + clientResponse.statusCode()
                                );
                            })
                    .bodyToMono(KakaoBookResponse.class)
                    .block();

            if (response == null || response.documents() == null) {
                return Collections.emptyList();
            }

            return response.documents().stream()
                    .map(doc -> new BookDto(
                            extractIsbn(doc.isbn()),
                            doc.title(),
                            String.join(", ", doc.authors()),
                            doc.publisher(),
                            doc.thumbnail(),
                            null,
                            doc.price() == null ? null : doc.price().doubleValue()
                    ))
                    .collect(Collectors.toList());
        } catch (Exception e) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "Kakao API 검색 실패: " + e.getMessage()
            );
        }
    }

    private List<BookDto> searchAladin(String query) {
        if (aladinTtbKey == null || aladinTtbKey.isBlank()) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Aladin API key not configured");
        }

        try {
            // 🔥 하드코딩: ISBN 감지 및 무조건 13자리로 변환
            String normalizedQuery = query.replaceAll("[^0-9]", "");
            final String queryType;  // final로 선언
            final String searchQuery;  // final로 선언

            // ISBN-10 → ISBN-13 변환 (하드코딩)
            if (normalizedQuery.length() == 10) {
                String isbn13 = convertIsbn10ToIsbn13(normalizedQuery);
                if (isbn13 != null) {
                    queryType = "ISBN13";  // 🔥 하드코딩: 무조건 ISBN13
                    searchQuery = isbn13;
                } else {
                    queryType = "Title";
                    searchQuery = query;
                }
            }
            // ISBN-13 그대로 사용 (하드코딩)
            else if (normalizedQuery.length() == 13) {
                queryType = "ISBN13";  // 🔥 하드코딩: 무조건 ISBN13
                searchQuery = normalizedQuery;
            }
            // 제목 검색
            else {
                queryType = "Title";
                searchQuery = query;
            }

            // 📚 페이징: 최대 50권까지 가져오기 (알라딘 MaxResults는 최대 50)
            List<BookDto> allBooks = new java.util.ArrayList<>();
            int maxResults = 50;  // 한 번에 최대 50개
            int start = 1;

            AladinItemSearchResponse response = webClient.get()
                    .uri(uriBuilder -> uriBuilder
                            .scheme("https")
                            .host("www.aladin.co.kr")
                            .path("/ttb/api/ItemSearch.aspx")
                            .queryParam("ttbkey", aladinTtbKey)
                            .queryParam("Query", searchQuery)
                            .queryParam("QueryType", queryType)
                            .queryParam("SearchTarget", "Book")
                            .queryParam("MaxResults", maxResults)
                            .queryParam("start", start)
                            .queryParam("output", "js")
                            .queryParam("Version", "20131101")
                            .build())
                    .retrieve()
                    .onStatus(status -> status.is4xxClientError() || status.is5xxServerError(),
                            clientResponse -> {
                                throw new ResponseStatusException(
                                        HttpStatus.BAD_GATEWAY,
                                        "Aladin API 호출 실패: " + clientResponse.statusCode()
                                );
                            })
                    .bodyToMono(AladinItemSearchResponse.class)
                    .block();

            if (response == null || response.item() == null) {
                return Collections.emptyList();
            }

            List<BookDto> books = response.item().stream()
                    .map(item -> new BookDto(
                            item.isbn13() != null && !item.isbn13().isBlank() ? item.isbn13() : item.isbn(),
                            item.title(),
                            item.author(),
                            item.publisher(),
                            item.cover(),
                            null,
                            item.priceSales() == null ? null : item.priceSales().doubleValue()
                    ))
                    .collect(Collectors.toList());

            allBooks.addAll(books);

            return allBooks;
        } catch (Exception e) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "Aladin API 검색 실패: " + e.getMessage()
            );
        }
    }

    /**
     * ISBN-10을 ISBN-13으로 변환
     * @param isbn10 10자리 ISBN
     * @return 13자리 ISBN (변환 실패 시 null)
     */
    private String convertIsbn10ToIsbn13(String isbn10) {
        if (isbn10 == null || isbn10.length() != 10) {
            return null;
        }

        try {
            // ISBN-10의 마지막 체크 디지트 제거하고 978 접두어 추가
            String base = "978" + isbn10.substring(0, 9);

            // ISBN-13 체크 디지트 계산
            int sum = 0;
            for (int i = 0; i < 12; i++) {
                int digit = Character.getNumericValue(base.charAt(i));
                // 홀수 위치(0-based)는 3을 곱함
                sum += (i % 2 == 0) ? digit : digit * 3;
            }

            int checkDigit = (10 - (sum % 10)) % 10;
            String isbn13 = base + checkDigit;

            return isbn13;
        } catch (Exception e) {
            return null;
        }
    }

    private String extractIsbn(String raw) {
        if (raw == null) {
            return "";
        }
        String[] parts = raw.split("\\s+");
        return parts.length > 0 ? parts[0] : raw;
    }
}

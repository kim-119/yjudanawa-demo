package yju.danawa.com.service;

import yju.danawa.com.domain.Book;
import yju.danawa.com.dto.BookDto;
import yju.danawa.com.repository.BookRepository;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    @Cacheable(cacheNames = "books", key = "#keyword")
    public List<BookDto> search(String keyword) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return Collections.emptyList();
        }
        String normalized = keyword.trim();
        List<Book> books = bookRepository.searchByKeyword(normalized);
        return books.stream()
                .map(book -> new BookDto(
                        book.getIsbn(),
                        book.getTitle(),
                        book.getAuthor(),
                        book.getPublisher(),
                        book.getImageUrl(),
                        book.getPublishedDate(),
                        book.getPrice()
                ))
                .collect(Collectors.toList());
    }
}

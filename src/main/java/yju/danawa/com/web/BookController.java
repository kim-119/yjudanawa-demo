package yju.danawa.com.web;

import yju.danawa.com.dto.BookDto;
import yju.danawa.com.dto.BookPriceDto;
import yju.danawa.com.service.BookService;
import yju.danawa.com.service.BookPriceService;
import yju.danawa.com.service.YjuLibraryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookService bookService;
    private final YjuLibraryService yjuLibraryService;
    private final BookPriceService bookPriceService;

    public BookController(BookService bookService, YjuLibraryService yjuLibraryService, BookPriceService bookPriceService) {
        this.bookService = bookService;
        this.yjuLibraryService = yjuLibraryService;
        this.bookPriceService = bookPriceService;
    }

    @GetMapping("/search")
    public BookSearchResponse getBooks(@RequestParam("q") String keyword) {
        List<BookDto> items = bookService.search(keyword);
        return new BookSearchResponse(items, items.size());
    }

    @GetMapping("/library-check")
    public YjuLibraryService.LibraryAvailability checkLibrary(
            @RequestParam(value = "isbn", required = false) String isbn,
            @RequestParam(value = "title", required = false) String title,
            @RequestParam(value = "author", required = false) String author,
            @RequestParam(value = "publisher", required = false) String publisher) {

        // 저자, 출판사 정보가 있으면 상세 검색 사용
        if ((author != null && !author.isBlank()) || (publisher != null && !publisher.isBlank())) {
            return yjuLibraryService.checkAvailabilityWithDetails(isbn, title, author, publisher);
        }

        // 기본 검색 (ISBN 또는 제목만)
        return yjuLibraryService.checkAvailability(isbn, title);
    }

    @GetMapping("/prices")
    public List<BookPriceDto> getBookPrices(
            @RequestParam(value = "isbn", required = false) String isbn,
            @RequestParam(value = "title", required = false) String title) {
        return bookPriceService.getPrices(isbn, title);
    }

    public record BookSearchResponse(List<BookDto> items, int total) {}
}



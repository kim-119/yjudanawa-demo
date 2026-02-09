import api from "./api";

const cacheTtlMs = 5 * 60 * 1000;
const cache = new Map<string, { expiresAt: number; data: any }>();

const getCached = (key: string) => {
  const entry = cache.get(key);
  if (!entry) return undefined;
  if (Date.now() > entry.expiresAt) {
    cache.delete(key);
    return undefined;
  }
  return entry.data;
};

const setCached = (key: string, data: any) => {
  cache.set(key, { expiresAt: Date.now() + cacheTtlMs, data });
};

export interface BookQueryParams {
  keyword: string;
}

interface BookSearchResponse<T> {
  items: T[];
  total: number;
}

export interface LibraryAvailability {
  found: boolean;
  available: boolean;
  location?: string;
  callNumber?: string;
  detailUrl: string;
  errorMessage?: string;
}

export interface BookPrice {
  store: string;
  storeName: string;
  price: number | null;
  url: string;
  deliveryInfo: string | null;
  available: boolean;
}

export const getBooks = async (keyword: string) => {
  const key = `books:${keyword}`;
  const cached = getCached(key);
  if (cached) return cached;
  const response = await api.get<BookSearchResponse<any>>("/books/search", {
    params: { q: keyword },
  });
  const items = response.data?.items ?? [];
  setCached(key, items);
  return items;
};

export const searchExternalBooks = async (
  query: string,
  source: "kakao" | "aladin" | "auto" = "kakao"
) => {
  const key = `external:${source}:${query}`;
  const cached = getCached(key);
  if (cached) return cached;
  const response = await api.get("/external/books", {
    params: { query, source },
  });
  // Normalize response: always return array
  const items = Array.isArray(response.data) ? response.data : [];
  setCached(key, items);
  return items;
};

export const checkLibraryAvailability = async (
  isbn?: string,
  title?: string,
  author?: string,
  publisher?: string
): Promise<LibraryAvailability> => {
  const key = `library:${isbn}:${title}:${author}:${publisher}`;
  const cached = getCached(key);
  if (cached) return cached;

  const response = await api.get<LibraryAvailability>("/books/library-check", {
    params: {
      isbn,
      title,
      author,
      publisher
    },
  });

  setCached(key, response.data);
  return response.data;
};

export const getBookPrices = async (
  isbn?: string,
  title?: string
): Promise<BookPrice[]> => {
  const key = `prices:${isbn}:${title}`;
  const cached = getCached(key);
  if (cached) return cached;

  const response = await api.get<BookPrice[]>("/books/prices", {
    params: {
      isbn,
      title
    },
  });

  setCached(key, response.data);
  return response.data;
};

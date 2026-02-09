<template>
  <div class="min-h-screen bg-white text-slate-900 transition-colors dark:bg-slate-950 dark:text-slate-100">
    <header class="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-6">
      <div class="text-xl font-extrabold tracking-[0.2em] text-brand-green">Y-DANAWA</div>
      <div class="flex items-center gap-3">
        <button
          class="rounded-full border border-slate-200 px-4 py-2 text-xs text-slate-600 dark:border-slate-800 dark:text-slate-300"
          @click="toggleDark"
        >
          {{ isDark ? "라이트" : "다크" }}
        </button>
      </div>
    </header>

    <main class="mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 pb-24">
      <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex w-full items-center rounded-full border border-slate-200 bg-white px-4 py-2 shadow-sm dark:border-slate-800 dark:bg-slate-950">
            <input
              v-model="searchQuery"
              placeholder="도서명/저자/출판사 검색"
              class="w-full border-none bg-transparent text-sm text-slate-800 outline-none dark:text-slate-100"
              @keyup.enter="onSearch"
            />
            <button
              class="ml-2 rounded-full border border-slate-200 px-4 py-2 text-xs text-slate-600 dark:border-slate-700 dark:text-slate-300"
              @click="onSearch"
            >
              검색
            </button>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-500">
          <span v-if="isLoading">검색 중...</span>
          <span v-else-if="hasSearched">총 {{ displayResults.length }}건</span>
        </div>
      </section>

      <div v-if="errorMsg" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">
        {{ errorMsg }}
      </div>
      <div v-if="externalWarning" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
        {{ externalWarning }}
      </div>
      <div
        v-if="hasSearched && !isLoading && displayResults.length === 0"
        class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600"
      >
        검색 결과가 없습니다.
      </div>

      <section class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="book in displayResults"
          :key="bookKey(book)"
          class="flex flex-col gap-4 rounded-3xl border border-slate-100 bg-white p-5 shadow-sm dark:border-slate-900 dark:bg-slate-900"
        >
          <img
            :src="book.imageUrl || fallbackCover"
            :alt="book.title"
            class="h-56 w-full rounded-2xl object-cover shadow"
            @error="onImageError"
          />
          <div class="flex flex-col gap-2">
            <h3 class="text-base font-semibold">{{ book.title }}</h3>
            <p class="text-xs text-slate-500">{{ book.author }} · {{ book.publisher }}</p>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-200">
              {{ formatPrice(book.price) }}
            </p>
          </div>

          <!-- 영진전문대 도서관 소장 정보 -->
          <div
            v-if="libraryStatus[bookKey(book)]"
            class="rounded-xl border px-3 py-2 text-xs"
            :class="getLibraryStatusClass(libraryStatus[bookKey(book)])"
          >
            <div class="flex items-center justify-between">
              <span class="font-semibold">🏫 영진전문대 도서관</span>
              <a
                :href="libraryStatus[bookKey(book)].detailUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="text-blue-600 hover:underline font-medium"
              >
                확인
              </a>
            </div>
            <div class="mt-1 text-xs font-medium">
              {{ getLibraryStatusText(libraryStatus[bookKey(book)]) }}
            </div>
          </div>

          <div class="mt-auto flex gap-2 text-xs">
            <a
              class="flex-1 rounded-full border border-slate-200 px-3 py-2 text-center text-slate-600 hover:border-brand-orange hover:text-brand-orange dark:border-slate-800"
              :href="toYes24(book)"
              target="_blank"
              rel="noopener"
            >
              YES24
            </a>
            <a
              class="flex-1 rounded-full border border-slate-200 px-3 py-2 text-center text-slate-600 hover:border-blue-500 hover:text-blue-500 dark:border-slate-800"
              :href="toAladin(book)"
              target="_blank"
              rel="noopener"
            >
              알라딘
            </a>
            <a
              class="flex-1 rounded-full border border-slate-200 px-3 py-2 text-center text-slate-600 hover:border-brand-green hover:text-brand-green dark:border-slate-800"
              :href="toKyobo(book)"
              target="_blank"
              rel="noopener"
            >
              교보문고
            </a>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { getBooks, searchExternalBooks, checkLibraryAvailability, type LibraryAvailability } from "../api/bookApi";

interface BookSummary {
  isbn?: string;
  title: string;
  author: string;
  publisher: string;
  imageUrl?: string;
  publishedDate?: string;
  price?: number | null;
}

const searchQuery = ref("");
const hasSearched = ref(false);
const isLoading = ref(false);
const errorMsg = ref("");
const externalWarning = ref("");
const displayResults = ref<BookSummary[]>([]);
const isDark = ref(false);
const libraryStatus = ref<Record<string, LibraryAvailability>>({});

const fallbackCover =
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='420'><rect width='100%' height='100%' fill='%23f1f5f9'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-size='14'>No Image</text></svg>";

const toggleDark = () => {
  isDark.value = !isDark.value;
  document.documentElement.classList.toggle("dark", isDark.value);
};

const resetSearchState = () => {
  hasSearched.value = false;
  isLoading.value = false;
  errorMsg.value = "";
  externalWarning.value = "";
  displayResults.value = [];
  libraryStatus.value = {};
};

watch(searchQuery, (value) => {
  if (!value.trim()) {
    resetSearchState();
  }
});

const onSearch = async () => {
  const keyword = searchQuery.value.trim();
  if (!keyword) {
    resetSearchState();
    return;
  }

  hasSearched.value = true;
  isLoading.value = true;
  errorMsg.value = "";
  externalWarning.value = "";
  displayResults.value = [];
  libraryStatus.value = {};

  const [dbResult, externalResult] = await Promise.allSettled([
    getBooks(keyword),
    searchExternalBooks(keyword, "auto"),
  ]);

  const dbItems = dbResult.status === "fulfilled" ? dbResult.value : [];

  const externalItems =
    externalResult.status === "fulfilled" ? externalResult.value : [];
  if (externalResult.status === "rejected") {
    externalWarning.value = buildErrorMessage("외부 API 검색 실패", externalResult.reason);
  }

  displayResults.value = mergeResults(dbItems, externalItems);
  isLoading.value = false;

  // 도서관 소장 확인 (백그라운드)
  checkLibraryForAllBooks();
};

const checkLibraryForAllBooks = async () => {
  for (const book of displayResults.value) {
    const key = bookKey(book);
    try {
      const status = await checkLibraryAvailability(
        book.isbn,
        book.title,
        book.author,
        book.publisher
      );
      libraryStatus.value[key] = status;
    } catch (error) {
      console.warn(`도서관 확인 실패: ${book.title}`, error);
    }
  }
};

const mergeResults = (dbItems: BookSummary[], externalItems: BookSummary[]) => {
  const merged: BookSummary[] = [];
  const seen = new Set<string>();

  const pushUnique = (item: BookSummary) => {
    const key = bookKey(item);
    if (!seen.has(key)) {
      seen.add(key);
      merged.push(item);
    }
  };

  dbItems.forEach(pushUnique);
  externalItems.forEach(pushUnique);

  return merged;
};

const bookKey = (book: BookSummary) => {
  if (book.isbn) return `isbn:${book.isbn}`;
  return `meta:${book.title}|${book.author}|${book.publisher}`;
};

const buildErrorMessage = (label: string, error: any) => {
  const status = extractStatus(error);
  if (status) return `${label} (status: ${status})`;
  return `${label} (status: unknown)`;
};

const extractStatus = (error: any) => {
  return error?.response?.status || error?.status;
};

const formatPrice = (price?: number | null) => {
  if (price === null || price === undefined) return "가격 정보 없음";
  return `${price.toLocaleString()}원`;
};

const toYes24 = (book: BookSummary) => {
  const keyword = book.isbn || book.title;
  return `https://www.yes24.com/Product/Search?domain=BOOK&query=${encodeURIComponent(keyword)}`;
};

const toAladin = (book: BookSummary) => {
  const keyword = book.isbn || book.title;
  return `https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&SearchWord=${encodeURIComponent(keyword)}`;
};

const toKyobo = (book: BookSummary) => {
  const keyword = book.isbn || book.title;
  return `https://search.kyobobook.co.kr/search?keyword=${encodeURIComponent(keyword)}`;
};

const getLibraryStatusClass = (status: LibraryAvailability) => {
  if (!status.found) {
    return "border-slate-200 bg-slate-50 text-slate-600";
  }
  if (status.available) {
    return "border-green-200 bg-green-50 text-green-700";
  }
  return "border-amber-200 bg-amber-50 text-amber-700";
};

const getLibraryStatusText = (status: LibraryAvailability) => {
  if (!status.found) {
    return "소장 정보 없음";
  }
  if (status.available) {
    const loc = status.location ? ` (${status.location})` : "";
    return `✅ 소장 중 - 대출 가능${loc}`;
  }
  return "⏳ 소장 중 - 대출 중";
};

const onImageError = (event: Event) => {
  const target = event.target as HTMLImageElement | null;
  if (target) target.src = fallbackCover;
};
</script>


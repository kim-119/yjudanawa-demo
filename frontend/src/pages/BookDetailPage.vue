<template>
  <div class="min-h-screen bg-white text-slate-900 transition-colors dark:bg-slate-950 dark:text-slate-100">
    <header class="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-6">
      <div class="text-xl font-extrabold tracking-[0.2em] text-brand-green">Y-DANAWA</div>
      <div class="flex w-full max-w-xl items-center rounded-full border border-slate-200 bg-white px-4 py-2 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <input
          v-model="searchQuery"
          placeholder="ISBN/도서명 검색"
          class="w-full border-none bg-transparent text-sm text-slate-800 outline-none dark:text-slate-100"
          @keyup.enter="onSearch"
        />
        <button class="text-slate-500 dark:text-slate-400" aria-label="voice search">
          <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current">
            <path
              d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V20H9v2h6v-2h-2v-2.08A7 7 0 0 0 19 11h-2z"
            />
          </svg>
        </button>
        <button
          class="ml-2 rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 dark:border-slate-700 dark:text-slate-300"
          @click="onSearch"
        >
          검색
        </button>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="rounded-full border border-slate-200 px-4 py-2 text-xs text-slate-600 dark:border-slate-800 dark:text-slate-300"
          @click="toggleDark"
        >
          {{ isDark ? "라이트" : "다크" }}
        </button>
        <button class="rounded-full bg-brand-green px-5 py-2 text-sm font-semibold text-white shadow">로그인</button>
      </div>
    </header>

    <div class="mx-auto grid w-full max-w-7xl gap-6 px-6 pb-24 lg:grid-cols-[220px_1fr_240px]">
      <aside class="flex flex-col gap-6">
        <nav class="flex flex-col gap-3">
          <button class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm dark:border-slate-900 dark:bg-slate-900">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-brand-blue dark:bg-slate-800">
              <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current">
                <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4zm0 2c-4 0-7 2-7 5v1h14v-1c0-3-3-5-7-5z" />
              </svg>
            </span>
            마이페이지
          </button>
          <button class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm dark:border-slate-900 dark:bg-slate-900">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-amber-50 text-brand-orange dark:bg-slate-800">
              <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current">
                <path d="M7 4h-2l-2 4v2h2l3.6 7.59L7.25 20H19v-2H8.42l1.1-2H17a2 2 0 0 0 1.8-1.1L22 8H6.21l-.94-2z" />
              </svg>
            </span>
            장바구니/결제
          </button>
          <button class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm dark:border-slate-900 dark:bg-slate-900">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current">
                <path d="M4 4h12a2 2 0 0 1 2 2v12H4a2 2 0 0 0-2 2V6a2 2 0 0 1 2-2zm0 14h14V6H4z" />
              </svg>
            </span>
            자료실
          </button>
          <button class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm dark:border-slate-900 dark:bg-slate-900">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current">
                <path d="M4 4h16v10H5.17L4 15.17V4zm0 13l4-4h12v7H4z" />
              </svg>
            </span>
            Q&amp;A
          </button>
        </nav>

        <section class="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-100">인기 도서</h3>
          <ol class="mt-3 space-y-2 text-xs text-slate-500">
            <li>1. 데이터 구조와 알고리즘</li>
            <li>2. 머신러닝 핸드북</li>
            <li>3. 인공지능 개론</li>
          </ol>
        </section>

        <section class="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-100">SNS</h3>
          <div class="mt-3 flex gap-3 text-slate-500">
            <a href="#" aria-label="facebook" class="rounded-full bg-slate-100 p-2 hover:text-brand-blue dark:bg-slate-800">
              <svg viewBox="0 0 24 24" class="h-4 w-4 fill-current">
                <path d="M13 22v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3V2h-3a5 5 0 0 0-5 5v3H6v4h3v8z" />
              </svg>
            </a>
            <a href="#" aria-label="twitter" class="rounded-full bg-slate-100 p-2 hover:text-sky-500 dark:bg-slate-800">
              <svg viewBox="0 0 24 24" class="h-4 w-4 fill-current">
                <path d="M22 5.8a8.2 8.2 0 0 1-2.4.7A4.1 4.1 0 0 0 21.4 4a8.5 8.5 0 0 1-2.7 1A4.2 4.2 0 0 0 11.8 9a12 12 0 0 1-8.7-4.4A4.2 4.2 0 0 0 4 10.4a4.1 4.1 0 0 1-1.9-.5v.1a4.2 4.2 0 0 0 3.3 4.1 4.1 4.1 0 0 1-1.9.1 4.2 4.2 0 0 0 3.9 2.9A8.4 8.4 0 0 1 2 19.4 12 12 0 0 0 8.3 21c7.4 0 11.4-6.2 11.4-11.6v-.5A8 8 0 0 0 22 5.8z" />
              </svg>
            </a>
            <a href="#" aria-label="instagram" class="rounded-full bg-slate-100 p-2 hover:text-pink-500 dark:bg-slate-800">
              <svg viewBox="0 0 24 24" class="h-4 w-4 fill-current">
                <path d="M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4zm5 4a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm6.5-.9a1.1 1.1 0 1 0 1.1 1.1 1.1 1.1 0 0 0-1.1-1.1z" />
              </svg>
            </a>
          </div>
        </section>
      </aside>

      <main class="flex flex-col gap-6">
        <nav class="text-xs text-slate-400">홈 &gt; 도서</nav>

        <div v-if="searchState.message" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
          {{ searchState.message }}
        </div>
        <div v-if="searchState.error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">
          {{ searchState.error }}
        </div>

        <section class="grid gap-6 rounded-3xl bg-white p-6 shadow-lg dark:bg-slate-900 md:grid-cols-[180px_1fr]">
          <img
            class="h-[240px] w-[180px] rounded-2xl object-cover shadow-lg"
            :src="coverUrl"
            alt="book cover"
            @error="onCoverError"
          />
          <div class="flex flex-col gap-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <h1 class="text-2xl font-semibold">{{ book.title }}</h1>
              <div class="flex items-center gap-2 text-sm text-amber-500">
                <span>★</span>
                <strong>{{ book.rating }}</strong>
                <span class="text-slate-400">({{ book.reviews }} 리뷰)</span>
              </div>
            </div>
            <p class="text-sm text-slate-500">{{ book.author }} · {{ book.publisher }}</p>

            <div class="grid gap-3 lg:grid-cols-3">
              <button
                class="flex flex-col gap-1 rounded-2xl bg-brand-blue px-5 py-4 text-left text-white shadow"
                @click="handleOpenLink('영진 중앙도서관', deepLinks.loan)"
              >
                도서관 대출
                <span class="w-fit rounded-full bg-white/20 px-3 py-1 text-xs">중앙도서관</span>
              </button>
              <button
                class="flex flex-col gap-1 rounded-2xl bg-brand-orange px-5 py-4 text-left text-white shadow"
                @click="handleOpenLink('YES24', deepLinks.yes24)"
              >
                YES24 구매
                <span class="text-sm">{{ book.yes24Price }}</span>
              </button>
              <button
                class="flex flex-col gap-1 rounded-2xl bg-brand-green px-5 py-4 text-left text-white shadow"
                @click="handleOpenLink('교보문고', deepLinks.kyobo)"
              >
                교보문고 구매
                <span class="text-sm">{{ book.kyoboPrice }}</span>
              </button>
            </div>

            <div class="flex flex-wrap gap-2 text-xs text-slate-500">
              <button
                class="rounded-full border border-slate-200 bg-white px-3 py-1 dark:border-slate-800 dark:bg-slate-900"
                @click="handleOpenLink('영진 전자도서관', deepLinks.yjcEbook)"
              >
                영진 전자도서관 바로가기
              </button>
            </div>

            <div class="mt-2 flex flex-col gap-2 rounded-2xl border border-slate-100 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              <div class="flex items-center justify-between">
                <span>시간-비용 가중치</span>
                <span>{{ sliderValue.toFixed(2) }}</span>
              </div>
              <input v-model.number="sliderValue" type="range" min="0" max="1" step="0.01" />
              <p v-if="logError" class="text-red-500">{{ logError }}</p>
            </div>
          </div>
        </section>

        <!-- 도서관 재고 정보 -->
        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold mb-4">🏫 도서관 재고 정보</h2>
          <div v-if="libraryLoading" class="text-center py-6">
            <div class="flex flex-col items-center gap-3">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-blue"></div>
              <p class="text-slate-600 dark:text-slate-400">영진전문대 도서관 재고 확인 중...</p>
              <p class="text-xs text-slate-500">잠시만 기다려주세요</p>
            </div>
          </div>
          <div v-else-if="libraryAvailability">
            <div v-if="libraryAvailability.found" class="rounded-2xl border p-4" :class="libraryAvailability.available ? 'border-green-200 bg-green-50 dark:bg-green-950' : 'border-red-200 bg-red-50 dark:bg-red-950'">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span class="text-2xl">{{ libraryAvailability.available ? '✅' : '📕' }}</span>
                  <div>
                    <p class="font-semibold" :class="libraryAvailability.available ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'">
                      {{ libraryAvailability.available ? '✨ 대출 가능' : '📚 대출 중' }}
                    </p>
                    <p v-if="libraryAvailability.location" class="text-sm text-slate-600 dark:text-slate-400">
                      📍 위치: {{ libraryAvailability.location }}
                    </p>
                    <p v-if="libraryAvailability.callNumber" class="text-sm text-slate-600 dark:text-slate-400">
                      🔢 청구기호: {{ libraryAvailability.callNumber }}
                    </p>
                  </div>
                </div>
                <button
                  @click="handleOpenLink('영진 도서관 상세', libraryAvailability.detailUrl)"
                  class="rounded-full bg-brand-blue px-4 py-2 text-sm text-white hover:bg-blue-600"
                >
                  상세보기
                </button>
              </div>
            </div>
            <div v-else class="rounded-2xl border border-amber-200 bg-amber-50 p-4 dark:bg-amber-950">
              <div class="flex items-center gap-3">
                <span class="text-2xl">⚠️</span>
                <div>
                  <p class="font-semibold text-amber-700 dark:text-amber-300">도서관에 소장되어 있지 않습니다</p>
                  <p class="text-sm text-slate-600 dark:text-slate-400">아래 온라인 서점에서 구매하실 수 있습니다</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 가격 비교 (다나와 스타일) -->
        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold mb-4">💰 온라인 서점 가격 비교</h2>
          <div v-if="pricesLoading" class="text-center py-8 text-slate-500">
            <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-brand-green border-r-transparent"></div>
            <p class="mt-2">가격 정보 불러오는 중...</p>
          </div>
          <div v-else-if="bookPrices.length > 0" class="space-y-3">
            <div
              v-for="(price, index) in bookPrices"
              :key="price.store"
              class="flex flex-col gap-3 rounded-2xl border p-4 transition-all hover:shadow-md md:flex-row md:items-center md:justify-between"
              :class="[
                price.price !== null
                  ? 'border-slate-200 bg-slate-50 hover:border-brand-green dark:border-slate-800 dark:bg-slate-950'
                  : 'border-slate-100 bg-white dark:border-slate-900 dark:bg-slate-900',
                price.price !== null && price.price === lowestPrice ? 'ring-2 ring-brand-green ring-offset-2' : ''
              ]"
            >
              <div class="flex items-center gap-4">
                <div
                  class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-lg font-bold"
                  :class="
                    price.price !== null && price.price === lowestPrice
                      ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-white shadow-lg'
                      : index === 0 && price.price !== null
                      ? 'bg-amber-100 text-amber-600'
                      : index === 1 && price.price !== null
                      ? 'bg-slate-200 text-slate-600'
                      : price.price !== null
                      ? 'bg-orange-100 text-orange-600'
                      : 'bg-slate-100 text-slate-400'
                  "
                >
                  <span v-if="price.price !== null && price.price === lowestPrice" class="text-sm">👑</span>
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <p class="font-semibold text-slate-800 dark:text-slate-100">{{ price.storeName }}</p>
                    <span v-if="price.price !== null && price.price === lowestPrice" class="rounded-full bg-brand-green px-2 py-0.5 text-xs font-bold text-white">
                      최저가
                    </span>
                  </div>
                  <p v-if="price.deliveryInfo && price.price" class="text-xs text-slate-500 mt-1">
                    📦 {{ price.deliveryInfo }}
                  </p>
                  <p v-if="!price.price" class="text-xs text-slate-400 mt-1">
                    실시간 가격 조회 실패 - 클릭하여 확인
                  </p>
                </div>
              </div>
              <div class="flex items-center justify-between gap-4 md:justify-end">
                <div class="text-right">
                  <div v-if="price.price" class="flex flex-col items-end">
                    <p class="text-2xl font-bold text-brand-green">
                      {{ price.price.toLocaleString() }}원
                    </p>
                    <p v-if="getPriceDifference(price.price)" class="text-xs text-red-500">
                      {{ getPriceDifference(price.price) }}
                    </p>
                  </div>
                  <p v-else class="text-sm font-medium text-slate-400">가격 확인 필요</p>
                </div>
                <button
                  @click="handleOpenLink(price.storeName, price.url)"
                  :class="[
                    'rounded-full px-5 py-2.5 text-sm font-semibold shadow transition-all',
                    price.price !== null
                      ? 'bg-brand-green text-white hover:bg-green-600'
                      : 'bg-slate-300 text-slate-600 hover:bg-slate-400 dark:bg-slate-700 dark:text-slate-300'
                  ]"
                >
                  {{ price.price !== null ? '구매하기' : '가격 확인' }}
                </button>
              </div>
            </div>

            <!-- 가격 정보 요약 -->
            <div v-if="lowestPrice" class="mt-4 grid gap-3 md:grid-cols-2">
              <div class="rounded-2xl bg-emerald-50 p-4 dark:bg-emerald-950">
                <p class="text-xs font-semibold text-emerald-700 dark:text-emerald-300">💚 최저가</p>
                <p class="mt-1 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {{ lowestPrice.toLocaleString() }}원
                </p>
              </div>
              <div class="rounded-2xl bg-blue-50 p-4 dark:bg-blue-950">
                <p class="text-xs font-semibold text-blue-700 dark:text-blue-300">💡 Tip</p>
                <p class="mt-1 text-xs text-blue-600 dark:text-blue-400">
                  실시간 가격은 변동될 수 있습니다. 구매 전 재확인을 권장합니다.
                </p>
              </div>
            </div>

            <div v-else class="mt-4 rounded-2xl bg-amber-50 p-4 dark:bg-amber-950">
              <p class="text-xs text-amber-700 dark:text-amber-300">
                ⚠️ 현재 실시간 가격 정보를 가져올 수 없습니다. 각 서점 버튼을 클릭하여 최신 가격을 확인해주세요.
              </p>
            </div>
          </div>
          <div v-else class="text-center py-8 text-slate-500">
            가격 정보를 불러올 수 없습니다
          </div>
        </section>

        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold">관련 도서</h2>
          <div class="mt-4 flex gap-4 overflow-x-auto pb-2">
            <div v-for="item in related" :key="item.id" class="min-w-[120px] text-center text-xs text-slate-500">
              <img :src="item.cover" :alt="item.title" class="h-40 w-28 rounded-xl object-cover shadow" />
              <p class="mt-2">{{ item.title }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold">유저 리뷰</h2>
          <div class="mt-4 flex flex-col gap-4">
            <div v-for="review in reviews" :key="review.id" class="flex gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-slate-950">
              <img :src="review.avatar" alt="profile" class="h-12 w-12 rounded-full object-cover" />
              <div class="flex flex-1 flex-col gap-2">
                <div class="flex items-center justify-between text-sm">
                  <strong>{{ review.name }}</strong>
                  <span class="text-amber-500">★ {{ review.rating }}</span>
                </div>
                <p class="text-sm text-slate-600 dark:text-slate-300">{{ review.comment }}</p>
                <button class="w-fit rounded-full border border-slate-200 bg-white px-4 py-1 text-xs dark:border-slate-800 dark:bg-slate-900">도움돼요 {{ review.helpful }}</button>
              </div>
            </div>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold">회원가입</h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <div class="grid gap-1">
              <input v-model="registerForm.username" @blur="onValidateUsername" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="아이디" />
              <span v-if="registerValidation.username" class="text-xs text-red-500">{{ registerValidation.username }}</span>
            </div>
            <input v-model="registerForm.password" type="password" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="비밀번호" />
            <input v-model="registerForm.email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="이메일" />
            <input v-model="registerForm.fullName" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="이름" />
            <input v-model="registerForm.department" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="학과" />
            <div class="grid gap-1">
              <input v-model="registerForm.studentId" @blur="onValidateStudentId" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="학번" />
              <span v-if="registerValidation.studentId" class="text-xs text-red-500">{{ registerValidation.studentId }}</span>
            </div>
            <input v-model="registerForm.phone" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="전화번호" />
          </div>
          <div class="mt-4 flex items-center gap-3">
            <button class="rounded-full bg-brand-green px-5 py-2 text-sm font-semibold text-white shadow" @click="onRegister" :disabled="registerState.loading">
              회원가입
            </button>
            <span v-if="registerState.message" class="text-xs text-emerald-600">{{ registerState.message }}</span>
            <span v-if="registerState.error" class="text-xs text-red-500">{{ registerState.error }}</span>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <h2 class="text-lg font-semibold">로그인</h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <input v-model="loginForm.username" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="아이디" />
            <input v-model="loginForm.password" type="password" class="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900" placeholder="비밀번호" />
          </div>
          <div class="mt-4 flex items-center gap-3">
            <button class="rounded-full bg-brand-green px-5 py-2 text-sm font-semibold text-white shadow" @click="onLogin" :disabled="loginState.loading">
              로그인
            </button>
            <span v-if="loginState.message" class="text-xs text-emerald-600">{{ loginState.message }}</span>
            <span v-if="loginState.error" class="text-xs text-red-500">{{ loginState.error }}</span>
          </div>
        </section>
      </main>

      <aside class="flex flex-col gap-6">
        <section class="rounded-3xl bg-emerald-50 p-5 shadow-sm dark:bg-emerald-950">
          <h3 class="text-sm font-semibold">추천 인류학 트렌드 리포트</h3>
          <p class="mt-2 text-xs text-slate-600 dark:text-slate-300">2026 최신 리포트 무료 공개</p>
          <button class="mt-3 rounded-lg bg-brand-green px-4 py-2 text-xs font-semibold text-white">바로 보기</button>
        </section>
        <section class="rounded-3xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-900 dark:bg-slate-900">
          <img :src="promoImage" alt="promo" class="rounded-2xl" />
        </section>
      </aside>
    </div>

    <button class="fixed bottom-6 right-6 rounded-full bg-brand-green px-5 py-3 text-sm font-semibold text-white shadow-lg">챗봇</button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { getBooks, searchExternalBooks, getBookPrices, checkLibraryAvailability, type BookPrice, type LibraryAvailability } from "../api/bookApi";
import { sendClickLog } from "../api/logApi";
import { loginUser, registerUser, validateRegister } from "../api/authApi";
import { setAuthToken } from "../api/api";

interface BookSummary {
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  imageUrl?: string;
  publishedDate?: string;
  price?: number;
}

const searchQuery = ref("자바의 정석");
const isDark = ref(false);
const sliderValue = ref(0.5);
const logError = ref("");

// 도서관 재고 상태
const libraryAvailability = ref<LibraryAvailability | null>(null);
const libraryLoading = ref(false);

// 가격 비교 상태
const bookPrices = ref<BookPrice[]>([]);
const pricesLoading = ref(false);

const book = ref({
  isbn: "",
  title: "도서 상세",
  author: "정보 없음",
  publisher: "정보 없음",
  rating: 4.6,
  reviews: 128,
  cover: "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=280&q=80",
  yes24Price: "19,800원",
  kyoboPrice: "21,600원",
});

const related = ref(
  [] as Array<{ id: number; title: string; cover: string }>
);

const reviews = [
  {
    id: 1,
    name: "이수현",
    rating: 4.8,
    comment: "설명이 친절하고 사례가 많아서 이해가 쉬웠어요.",
    helpful: 24,
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=80&q=80",
  },
  {
    id: 2,
    name: "박지훈",
    rating: 4.4,
    comment: "대학 과제에 바로 활용할 수 있는 내용이 많습니다.",
    helpful: 18,
    avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=80&q=80",
  },
  {
    id: 3,
    name: "정민서",
    rating: 4.7,
    comment: "관련 도서 추천이 유용했어요.",
    helpful: 12,
    avatar: "https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&w=80&q=80",
  },
];

const promoImage = "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=300&q=80";

const deepLinks = computed(() => {
  const keyword = book.value.title;
  const encoded = encodeURIComponent(keyword);
  return {
    loan: `https://lib.yjc.ac.kr/WebYJC/Aspx/search/searchresultTotal.aspx?otod1=${encoded}&otwa1=IDX&chkMType=otb&OutSearchKey=${encoded}`,
    yes24: `https://www.yes24.com/Product/Search?domain=BOOK&query=${encoded}`,
    kyobo: `https://search.kyobobook.co.kr/search?keyword=${encoded}`,
    yjcEbook: `https://ebook.yjc.ac.kr/search?query=${encoded}`,
  };
});

const toggleDark = () => {
  isDark.value = !isDark.value;
};

const searchState = ref({
  message: "",
  error: "",
});

const onSearch = async () => {
  const keyword = searchQuery.value.trim();
  searchState.value = { message: "", error: "" };
  if (!keyword) {
    searchState.value = { message: "검색어를 입력해주세요.", error: "" };
    return;
  }
  await loadBooks(keyword);
};

const fallbackCover = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='240'><rect width='100%' height='100%' fill='%23f1f5f9'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-size='12'>No Image</text></svg>";
const coverUrl = ref(book.value.cover || fallbackCover);

const onCoverError = () => {
  coverUrl.value = fallbackCover;
};

const applyBooks = (results: BookSummary[], message: string) => {
  const primary = results[0];
  book.value = {
    ...book.value,
    isbn: primary.isbn,
    title: primary.title,
    author: primary.author,
    publisher: primary.publisher,
    cover: primary.imageUrl || book.value.cover,
  };
  coverUrl.value = book.value.cover || fallbackCover;
  related.value = results.slice(1, 6).map((item, index) => ({
    id: index + 1,
    title: item.title,
    cover: item.imageUrl || fallbackCover,
  }));
  searchState.value = { message, error: "" };

  // 도서관 재고 및 가격 정보 조회
  loadLibraryAvailability();
  loadBookPrices();
};

const loadLibraryAvailability = async () => {
  if (!book.value.isbn && !book.value.title) {
    return;
  }

  libraryLoading.value = true;
  try {
    libraryAvailability.value = await checkLibraryAvailability(
      book.value.isbn,
      book.value.title,
      book.value.author,
      book.value.publisher
    );
  } catch (error) {
    console.error("도서관 재고 조회 실패:", error);
    libraryAvailability.value = null;
  } finally {
    libraryLoading.value = false;
  }
};

const loadBookPrices = async () => {
  if (!book.value.isbn && !book.value.title) {
    return;
  }

  pricesLoading.value = true;
  try {
    const prices = await getBookPrices(
      book.value.isbn,
      book.value.title
    );

    // 가격이 있는 것을 우선 정렬하고, 그 다음 가격 순으로 정렬
    bookPrices.value = prices.sort((a, b) => {
      // 가격이 있는 것을 우선
      if (a.price !== null && b.price === null) return -1;
      if (a.price === null && b.price !== null) return 1;

      // 둘 다 가격이 있으면 가격 순 (저렴한 순)
      if (a.price !== null && b.price !== null) {
        return a.price - b.price;
      }

      // 둘 다 가격이 없으면 원래 순서 유지
      return 0;
    });
  } catch (error) {
    console.error("가격 정보 조회 실패:", error);
    bookPrices.value = [];
  } finally {
    pricesLoading.value = false;
  }
};

// 최저가와 가격 차이 계산
const lowestPrice = computed(() => {
  const pricesWithValue = bookPrices.value.filter(p => p.price !== null);
  if (pricesWithValue.length === 0) return null;
  return Math.min(...pricesWithValue.map(p => p.price!));
});

const getPriceDifference = (price: number | null) => {
  if (price === null || lowestPrice.value === null) return null;
  const diff = price - lowestPrice.value;
  return diff > 0 ? `+${diff.toLocaleString()}원` : null;
};

const loadBooks = async (keyword: string) => {
  searchState.value = { message: "검색 중...", error: "" };

  let externalError = "";
  let externalResults: BookSummary[] = [];
  try {
    externalResults = (await searchExternalBooks(keyword, "auto")) as BookSummary[];
  } catch (error: any) {
    const status = error?.response?.status;
    const message = error?.response?.data?.message || error?.response?.data;
    console.error("외부 API 에러:", { status, message, error });

    if (status === 503) {
      externalError = "외부 도서 API 키 설정이 필요합니다.";
    } else if (status === 502) {
      externalError = `외부 도서 API 게이트웨이 오류 (502): ${message || '외부 API 서버 응답 없음'}`;
    } else if (status >= 500) {
      externalError = `외부 도서 API 서버 오류 (${status}): ${message || '서버 문제 발생'}`;
    } else if (status === 400) {
      externalError = "잘못된 검색 요청입니다.";
    } else {
      externalError = `외부 도서 API 호출 실패 (${status || 'NETWORK'}): ${message || '네트워크 오류'}`;
    }
  }

  if (externalResults.length > 0) {
    applyBooks(externalResults, "외부 API 결과를 표시합니다.");
    return;
  }

  try {
    const results = (await getBooks(keyword)) as BookSummary[];
    if (results.length > 0) {
      applyBooks(results, externalError ? "외부 API 실패로 DB 결과를 표시합니다." : "");
      return;
    }
  } catch (error: any) {
    searchState.value = { message: "", error: "검색 요청에 실패했습니다. 백엔드 실행 상태를 확인해주세요." };
    return;
  }

  if (externalError) {
    searchState.value = { message: "", error: externalError };
  } else {
    related.value = [];
    searchState.value = { message: "검색 결과가 없습니다.", error: "" };
  }
};

const registerForm = ref({
  username: "",
  password: "",
  email: "",
  fullName: "",
  department: "",
  studentId: "",
  phone: "",
});

const registerValidation = ref({
  username: "",
  studentId: "",
});

const registerState = ref({
  loading: false,
  message: "",
  error: "",
});

const onValidateUsername = async () => {
  registerValidation.value.username = "";
  if (!registerForm.value.username) return;
  const result = await validateRegister(registerForm.value.username, undefined);
  if (!result.usernameAvailable) {
    registerValidation.value.username = "이미 존재하는 아이디입니다.";
  }
};

const onValidateStudentId = async () => {
  registerValidation.value.studentId = "";
  if (!registerForm.value.studentId) return;
  const result = await validateRegister(undefined, registerForm.value.studentId);
  if (!result.studentIdAvailable) {
    registerValidation.value.studentId = "이미 등록된 학번입니다.";
  }
};

const onRegister = async () => {
  registerState.value = { loading: true, message: "", error: "" };
  if (!registerForm.value.username || !registerForm.value.password || !registerForm.value.studentId) {
    registerState.value = { loading: false, message: "", error: "아이디/비밀번호/학번은 필수입니다." };
    return;
  }
  if (registerValidation.value.username || registerValidation.value.studentId) {
    registerState.value = { loading: false, message: "", error: "중복 검사 오류를 확인해주세요." };
    return;
  }
  try {
    const result = await registerUser({
      username: registerForm.value.username,
      password: registerForm.value.password,
      email: registerForm.value.email || undefined,
      fullName: registerForm.value.fullName || undefined,
      department: registerForm.value.department || undefined,
      studentId: registerForm.value.studentId || undefined,
      phone: registerForm.value.phone || undefined,
    });
    localStorage.setItem("ydanawa_token", result.token);
    registerState.value = { loading: false, message: `${result.username} 가입 완료`, error: "" };
  } catch (error: any) {
    const status = error?.response?.status;
    const message = error?.response?.data?.message;
    if (status === 409 && message === "USERNAME_EXISTS") {
      registerState.value = { loading: false, message: "", error: "이미 존재하는 아이디입니다." };
    } else if (status === 409 && message === "STUDENT_ID_EXISTS") {
      registerState.value = { loading: false, message: "", error: "이미 등록된 학번입니다." };
    } else if (status === 409 && message === "PASSWORD_IN_USE") {
      registerState.value = { loading: false, message: "", error: "다른 사용자가 쓰는 비밀번호입니다." };
    } else {
      registerState.value = { loading: false, message: "", error: "회원가입에 실패했습니다." };
    }
  }
};

const loginForm = ref({
  username: "",
  password: "",
});

const loginState = ref({
  loading: false,
  message: "",
  error: "",
});

const onLogin = async () => {
  loginState.value = { loading: true, message: "", error: "" };
  try {
    const result = await loginUser({
      username: loginForm.value.username,
      password: loginForm.value.password,
    });
    localStorage.setItem("ydanawa_token", result.token);
    loginState.value = { loading: false, message: `${result.username} 로그인 완료`, error: "" };
  } catch (error: any) {
    const status = error?.response?.status;
    if (status === 401) {
      loginState.value = { loading: false, message: "", error: "아이디/비밀번호가 올바르지 않습니다." };
    } else if (status === 403) {
      loginState.value = { loading: false, message: "", error: "계정이 잠겼거나 비활성 상태입니다." };
    } else {
      loginState.value = { loading: false, message: "", error: "로그인에 실패했습니다." };
    }
  }
};

const handleOpenLink = async (channel: string, url: string) => {
  logError.value = "";
  try {
    if (book.value.isbn) {
      await sendClickLog({
        isbn: book.value.isbn,
        target_channel: channel,
        slider_value: sliderValue.value,
      });
    }
  } catch (error) {
    logError.value = "클릭 로그 전송 실패";
  }
  window.open(url, "_blank", "noopener");
};

watch(isDark, (value) => {
  document.documentElement.classList.toggle("dark", value);
});

onMounted(() => {
  document.documentElement.classList.toggle("dark", isDark.value);
  const savedToken = localStorage.getItem("ydanawa_token");
  if (savedToken) {
    setAuthToken(savedToken);
  }
  void loadBooks(searchQuery.value);
});
</script>


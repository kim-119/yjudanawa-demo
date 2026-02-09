-- 기본 샘플 데이터 (외부 API에서 추가 데이터 자동 로드)
INSERT INTO books (isbn, title, author, publisher, image_url, published_date, price)
VALUES
  ('9788966260959', '자바의 정석', '남궁성', '도우출판', 'https://image.aladin.co.kr/product/7608/24/cover500/8966260959_1.jpg', '2016-01-01', 32000)
ON CONFLICT (isbn) DO NOTHING;



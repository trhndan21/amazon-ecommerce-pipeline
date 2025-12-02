CREATE SCHEMA IF NOT EXISTS amazon;

CREATE TABLE IF NOT EXISTS amazon.amazon_sales (
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    discounted_price TEXT,
    actual_price TEXT,
    discount_percentage TEXT,
    rating TEXT,
    rating_count TEXT,
    about_product TEXT,
    user_id TEXT,
    user_name TEXT,
    review_id TEXT,
    review_title TEXT,
    review_content TEXT,
    img_link TEXT,
    product_link TEXT
);

COPY amazon.amazon_sales(product_id, product_name, category, discounted_price, actual_price, discount_percentage, rating, rating_count, about_product, user_id, user_name, review_id, review_title, review_content, img_link, product_link) 
FROM '/input_data/amazon_sales.csv' DELIMITER ','  CSV HEADER;
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_genre_page(genre_url):
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    }
    response = requests.get(genre_url, headers=custom_headers)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(genre_url))
    genre_doc = BeautifulSoup(response.text, 'html.parser')
    return genre_doc

def paginate_genre(genre_url):
    genre_pages = []
    while True:
        genre_doc = get_genre_page(genre_url)
        genre_pages.append(genre_doc)
        next_button = genre_doc.find('a', class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator')
        if not next_button:
            break
        genre_url = 'https://www.amazon.com' + next_button['href']
    return genre_pages

def scrape_genre(genre_url, path):
    if os.path.exists(path):
        print('The file {} already exists ... Skipping ...'.format(path))
        return
    genre_pages = paginate_genre(genre_url)
    genre_books = []
    for genre_doc in genre_pages:
        genre_books += get_genre_books(genre_doc)
    genre_df = pd.DataFrame(genre_books)
    genre_df.to_json(path, index=None)


def scrape_genre_books():
    print('Scraping list of book genres')
    genres_df = scrape_genres()
    os.makedirs('data', exist_ok=True)
    for index, row in genres_df.iterrows():
        print("Scraping books for the genre {}".format(row['genre_titles']))
        scrape_genre(row['genre_urls'], 'data/{}.json'.format(row['genre_titles']))


def genre_books_info(div_tags):

    Book_name_tags = div_tags.find('span', class_="a-size-medium a-color-base a-text-normal")
    Book_url_tags = 'https://www.amazon.com' + div_tags.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')['href']
    Author_name_tags = div_tags.find('a', class_="a-size-base")
    Book_publisher_tags = div_tags.find('span', class_="a-badge-label-inner a-text-ellipsis")
    Book_img_tags = div_tags.find('img')
    Book_publish_date_tags = div_tags.find('span', class_="a-size-base a-color-secondary a-text-normal")
    Book_rating_tags = div_tags.find('span', class_='a-size-base puis-normal-weight-text')
    Book_reviews_tags = div_tags.find('span', class_='a-size-base s-underline-text')
    Book_description_tags = div_tags.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-bold')
    Book_price_tags = div_tags.find('span', class_='a-offscreen')
    Book_category_tags = div_tags.find('a', class_='a-size-base a-link-normal s-underline-link-text s-link-style a-text-bold')
    return Book_name_tags, Book_url_tags, Author_name_tags, Book_publisher_tags, Book_img_tags, Book_publish_date_tags, Book_rating_tags, Book_reviews_tags, Book_description_tags, Book_price_tags, Book_category_tags

def get_genre_books(genre_doc):

    div_selection_class = 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'
    div_tags = genre_doc.find_all('div', class_=div_selection_class)

    genre_books_dict = {
        'Title': [],
        'previewLink': [],
        'authors': [],
        'publisher': [],
        'Book_img': [],
        'Book_publish_date': [],
        'Book_rating': [],
        'Book_reviews': [],
        'description': [],
        'price': [],
        'categories': []
    }

    for i in range(0, len(div_tags)):
        genre_info = genre_books_info(div_tags[i])

        if genre_info[0] is not None:
            genre_books_dict['Title'].append(genre_info[0].text)
        else:
            genre_books_dict['Title'].append('Missing')

        if genre_info[1] is not None:
            genre_books_dict['previewLink'].append(genre_info[1])
        else:
            genre_books_dict['previewLink'].append('Missing')

        if genre_info[2] is not None:
            genre_books_dict['authors'].append(genre_info[2].text)
        else:
            genre_books_dict['authors'].append('Missing')

        if genre_info[3] is not None:
            genre_books_dict['publisher'].append(genre_info[3].text)
        else:
            genre_books_dict['publisher'].append('Missing')

        if genre_info[4] is not None:
           genre_books_dict['Book_img'].append(genre_info[4]['src'])
        else:
            genre_books_dict['Book_img'].append('Missing')

        if genre_info[5] is not None:
            genre_books_dict['Book_publish_date'].append(genre_info[5].text)
        else:
            genre_books_dict['Book_publish_date'].append('Missing')

        if genre_info[6] is not None:
            genre_books_dict['Book_rating'].append(genre_info[6].text)
        else:
            genre_books_dict['Book_rating'].append('Missing')

        if genre_info[7] is not None:
            genre_books_dict['Book_reviews'].append(genre_info[7].text)
        else:
            genre_books_dict['Book_reviews'].append('Missing')

        if genre_info[8] is not None:
            genre_books_dict['description'].append(genre_info[8].text)
        else:
            genre_books_dict['description'].append('Missing')

        if genre_info[9] is not None:
            genre_books_dict['price'].append(genre_info[9].text)
        else:
            genre_books_dict['price'].append('Missing')

        if genre_info[10] is not None:
            genre_books_dict['categories'].append(genre_info[10].text)
        else:
            genre_books_dict['categories'].append('Missing')

    return pd.DataFrame(genre_books_dict)


def get_genre_info(doc):
    # Div with all genres
    div_selection_class = "a-section a-spacing-none"
    genre_div_tags = doc.find_all('div', class_=div_selection_class)
    # List of genres inside div
    genre_tags = genre_div_tags[2].find_all('a')

    genre_titles = []
    for i in range(0, len(genre_tags)):
        genre_titles.append(genre_tags[i].text)
    genre_urls = []
    base_url = 'https://www.amazon.com'
    for i in range(0, len(genre_tags)):
        genre_urls.append(base_url + genre_tags[i]['href'])
    return genre_titles, genre_urls

def scrape_genres():
    genre_url = 'https://www.amazon.com/Books/s?srs=17143709011&rh=n%3A283155'
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    }
    response = requests.get(genre_url, headers=custom_headers)
    if response.status_code != 200:
        raise Exception('Failed to load page {}', format(genre_url))
    doc = BeautifulSoup(response.text, 'html.parser')
    genre_dict = {
        'genre_titles': get_genre_info(doc)[0],
        'genre_urls': get_genre_info(doc)[1]
    }
    return pd.DataFrame(genre_dict)

if __name__ == "__main__":
    scrape_genre_books()



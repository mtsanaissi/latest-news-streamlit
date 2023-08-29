from selenium import webdriver
import streamlit as st
import time
from datetime import datetime, timedelta
import urllib.parse

# Mapping of month abbreviations to month numbers
month_mapping = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12
}

def parse_brazilian_date(date_str):
    date_parts = date_str.split()
    day = int(date_parts[0])
    month = month_mapping[date_parts[2].replace(".", "")]
    
    current_year = datetime.now().year
    
    if len(date_parts) == 5:
        year = int(date_parts[4])
    else:
        year = current_year
    
    return datetime(year, month, day)

def parse_custom_time(time_str):
    now = datetime.now()
    time_str = time_str.lower()
    
    if "hora" in time_str:
        hours_ago = int(time_str.split()[0])
        return now - timedelta(hours=hours_ago)
    elif "minuto" in time_str:
        minutes_ago = int(time_str.split()[0])
        return now - timedelta(minutes=minutes_ago)
    elif "ontem" in time_str:
        return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif "anteontem" in time_str:
        return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif "dias" in time_str:
        days_ago = int(time_str.split()[0])
        return now - timedelta(days=days_ago)
    else:
        try:
            return parse_brazilian_date(time_str)
        except ValueError:
            return datetime(2000, 1, 1)

def should_ignore(article):
    try:
        # Finds the element that holds the name of the source.
        # We ignore news from Zimbra, because it gives only unwanted spam.
        return article.find_element('css selector', "article > div > div > a").text == "Zimbra"
    except:
        return False

def scrape_news(driver, news_count):
    articles = []
    
    html_articles = driver.find_elements('css selector', "article")
    
    for i, article in enumerate(html_articles[:news_count]):
        if (should_ignore(article)):
            continue
        title = article.find_element('css selector', "article > h3 > a").text
        time = article.find_element('css selector', "article > div > div > time").text
        url = article.find_element('css selector', "article > h3 > a").get_attribute("href")
        articles.append({"title": title, "url": url, "time": time})
    return articles

# Create a Streamlit app to display the news.
def main():
    # Set selenium driver options
    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')

    # Create a Selenium driver.
    driver = webdriver.Firefox(options=options)

    if 'search_text' not in st.session_state:
        st.session_state.search_text = ''

    st.markdown("### Quero as últimas notícias sobre...")
    st.session_state.search_text = st.text_input("Assunto", key="search_text_input", placeholder="Especifique um assunto aqui", label_visibility="collapsed")
    st.session_state.search_text = urllib.parse.quote(st.session_state.search_text)

    st.button('Pesquisar')

    # Check if search_text is not null and not empty
    if st.session_state.search_text is not None and len(st.session_state.search_text.strip()) > 0:
        # Define the news source we want to track and get the driver there.
        news_source = f"https://news.google.com/search?q={st.session_state.search_text}&hl=pt-BR&gl=BR"
        driver.get(news_source)

        # Scroll down to the bottom of the page to load more news.
        loads = 0
        while loads < 1:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            loads += 1

        news_max = 20
        articles = scrape_news(driver, news_max)
        articles.sort(key=lambda x: parse_custom_time(x['time']), reverse=True)

        for article in articles:
            st.write(f"{article['time']} - [{article['title']}]({article['url']})")
        
        driver.quit()

if __name__ == "__main__":
    main()

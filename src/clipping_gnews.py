import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import streamlit as st
import time
from datetime import datetime, timedelta

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

def scrape_news(driver, news_count):
    articles = []
    
    html_articles = driver.find_elements(By.CSS_SELECTOR, "article")
    
    for i, article in enumerate(html_articles[:news_count]):
        title = article.find_element(By.CSS_SELECTOR, "article > h3 > a").text
        time = article.find_element(By.CSS_SELECTOR, "article > div > div > time").text
        url = article.find_element(By.CSS_SELECTOR, "article > h3 > a").get_attribute("href")
        articles.append({"title": title, "url": url, "time": time})
    return articles


# Create a Streamlit app to display the news.
def main():
    # Define the news source we want to track.
    news_source = "https://news.google.com/search?q=%22guar%C3%A1%22+bras%C3%ADlia&hl=pt-BR&gl=BR"

    # Create a Selenium driver.
    driver = webdriver.Edge()
    edge_options = webdriver.EdgeOptions()
    edge_options.use_webview = True
    edge_options.add_argument('--headless=new')

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

    st.title("Notícias do Guará-DF")

    for article in articles:
        st.write(f"{article['time']} - [{article['title']}]({article['url']})")
    
    driver.quit()

if __name__ == "__main__":
    main()
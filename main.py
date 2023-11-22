import smtplib
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

YOUTUBE_TRENDING_URL = 'https://www.youtube.com/feed/trending'


def get_driver():
    # Configure Chrome WebDriver options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_videos(driver):
    # Extract video elements from YouTube trending page
    VIDEO_DIV_TAG = 'ytd-video-renderer'
    driver.get(YOUTUBE_TRENDING_URL)
    time.sleep(5)
    videos = driver.find_elements(By.TAG_NAME, VIDEO_DIV_TAG)
    return videos


def parse_video(video):
    # Parse information from each video element
    title_tag = video.find_element(By.ID, 'video-title')
    title = title_tag.text
    url = title_tag.get_attribute('href')

    thumbnail_tag = video.find_element(By.TAG_NAME, 'img')
    thumbnail_url = thumbnail_tag.get_attribute('src')

    channel_div = video.find_element(By.CLASS_NAME, 'ytd-channel-name')
    channel_name = channel_div.text

    views_element = video.find_element(By.CLASS_NAME, 'inline-metadata-item')
    views_text = views_element.text

    description = video.find_element(By.ID, 'description-text').text

    return {
        'title': title,
        'url': url,
        'thumbnail_url': thumbnail_url,
        'channel': channel_name,
        'views': views_text,
        'description': description
    }


def send_email(attachment_path):
    # Configure email parameters
    sender = 'ravikumargokul440@gmail.com'
    receivers = ['gokul08r@gmail.com']
    subject = 'YouTube Trending Videos'

    # Create the MIMEMultipart object
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ', '.join(receivers)
    message['Subject'] = subject

    body = 'Top 10 trending videos on YouTube'

    # Attach text body
    message.attach(MIMEText(body, 'plain'))

    # Attach CSV file
    with open(attachment_path, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name="trending.csv")
        part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
        message.attach(part)

    try:
        # Connect to SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('mailid@gmail.com', 'password')
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error: {e}")
        print("Email could not be sent.")


if __name__ == "__main__":
    print('Creating driver')
    driver = get_driver()

    print('Fetching trending videos')
    videos = get_videos(driver)

    print(f'Found {len(videos)} videos')

    print('Parsing top 10 videos')
    videos_data = [parse_video(video) for video in videos[:10]]

    print('Save the data to a CSV')
    videos_df = pd.DataFrame(videos_data)
    csv_path = 'trending.csv'
    videos_df.to_csv(csv_path, index=None)

    print("Send the results over email")
    send_email(csv_path)

    print('Finished.')

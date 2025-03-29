import os
import pandas as pd
from datetime import datetime
import csv
import smtplib
import mimetypes
from email.message import EmailMessage
from bot import amazon_main 
from dotenv import load_dotenv


load_dotenv()

# emailing function
def send_email(output_filename, recipient_email):
    timestamp_now = datetime.now().strftime("Date: %d-%m-%Y TIME:%H:%M:%S")

    sender_email = os.getenv("SENDER_EMAIL")  
    sender_password = os.getenv("SENDER_PASSWORD") 
    subject = f"Amazon Scraped Data CSV for - {timestamp_now}"
    body = f"Please find the attached CSV file containing the scraped data dated - {timestamp_now}"

    # Create Email Message
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach CSV file
    with open(output_filename, "rb") as file:
        file_data = file.read()
        file_name = os.path.basename(output_filename)
        mime_type, _ = mimetypes.guess_type(output_filename)
        main_type, sub_type = mime_type.split("/") if mime_type else ("application", "octet-stream")
        msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=file_name)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main function
def main():
    csv_file_path = './fry_amazon_india_data.csv'  # Input CSV path

    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        exit()

    try:
        df = pd.read_csv(csv_file_path)
        asin_list = df.iloc[:, 0].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        exit()

    pincodes = ["400097", "110001","560001"]
    # ,"500001","600001","700002"
    
     
    city_map = {
        "400097": "mumbai",
        "110001": "delhi",
        "560001": "bangalore",
        "500001": "hyderabad",
        "201301": "noida",
        "600001": "Tamil Nadu",
        "700002": "kolkata",
    }
    host_url = "https://www.amazon.in/dp/"

    timestamp_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"./amazon_data/amazon_scraped_{timestamp_now}.csv"

    try:
        with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Asin','buy_box_flag' ,'Timestamp', 'Pincode', 'City', 'Seller', 'Price', 'coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price'])  # Header
        print(f"CSV header written to {output_filename}")
    except Exception as e:
        print(f"Error creating CSV: {e}")
        exit()

    amazon_main(pincodes, asin_list, host_url, output_filename, city_map)

    print(f"\nAll data written to {output_filename}")

    # Send email after CSV is created
    # recipient_emails = os.getenv("RECIPIENT_EMAIL")
    # send_email(output_filename, recipient_emails)

if __name__ == "__main__":
    main()

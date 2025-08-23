# backend/send_email.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from dotenv import load_dotenv
import os
import re
import smtplib

# Load env vars
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_USER = os.getenv("EMAIL_USER")
print("DEBUG:", EMAIL_USER, bool(SMTP_PASSWORD))

#RESOURCES_DIR = "resources"
RESOURCES_DIR = "/home/kumaresh/resources"

# --- Step 1: Normalize function (common use) ---
def normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text.lower())

# --- Step 2: Build lookup (still store actual filenames) ---
#def build_pdf_lookup(resources_dir="resources"):
#    return [f for f in os.listdir(resources_dir) if f.lower().endswith(".pdf")]

def build_pdf_lookup(resources_dir=RESOURCES_DIR):
    """
    Map normalized base name (before 'Program Details' chunk) -> actual filename.
    Handles any separators/spacing/case and trims trailing separators.
    """
    lookup = {}
    for filename in os.listdir(resources_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        base = os.path.splitext(filename)[0]

        # Split at first occurrence of 'program(me) details' with any separators
        # and ignore everything AFTER it (including trailing separators).
        parts = re.split(r'[_\-\s]*program(?:me)?[_\-\s]*details?[\s_\-]*', base, flags=re.IGNORECASE, maxsplit=1)
        core = parts[0] if parts else base

        key = normalize(core)
        if key:
            lookup[key] = filename
            # DEBUG: print what we built for each file
            print(f"📄 File '{filename}' -> key '{key}'")

    print(f"🔧 Built {len(lookup)} PDF keys")
    return lookup

pdf_lookup = build_pdf_lookup()
#pdf_files = build_pdf_lookup()


def send_skill_email(name, recipient, programs):
    if isinstance(programs, list):
        programs_text = ", ".join(programs) 
    else:
        programs_text = programs

    print("-------❄️❄️--------------------Inside send skill email 1")

    # Create multipart message
    msg = MIMEMultipart()
    msg["Subject"] = "Your Upskilling Resource"
    msg["From"] = formataddr(("Manipal Learning", EMAIL_USER))   
    msg["To"] = recipient

    
    html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Dear <strong>{name}</strong>,</p>
            <p>Thank you for showing interest in our learning programs.</p>
            <p>
              Attached the <strong>{programs_text}</strong> resource for your reference.
              Please go through the program description, outcomes, and topics at your convenience.
            </p>

            <p>For further assistance, feel free to contact us at <a href="mailto:{EMAIL_USER}">{EMAIL_USER}</a>.</p>
            <br>
            <p>Best regards,<br>
            UNext<br>
            Manipal Learning Team</p>
        </body>
        </html>
    """
    #alt.attach(MIMEText(html_body, "html"))
    msg.attach(MIMEText(html_body, "html"))

    # Attach PDF
    # Build PDF filename based on program_name
    # Example: "IOT" -> "IOT_Program_Details.pdf"
     # Attach PDFs for each program
    for program_name in (programs if isinstance(programs, list) else [programs]):
        program_key = normalize(program_name)
        print(f"🔍 Looking for '{program_name}' with key: {program_key}")
        pdf_filename = pdf_lookup.get(program_key)
        if not pdf_filename:
            print(f"⚠️ No PDF found for program: {program_name}")
            continue

        pdf_path = os.path.join(RESOURCES_DIR, pdf_filename)
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={pdf_filename}")
        msg.attach(part)
        print(f"✅ Attached: {pdf_filename} for program {program_name}")
    # --- Send Email ---
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
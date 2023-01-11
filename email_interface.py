import smtplib                                      
from email.mime.multipart import MIMEMultipart      
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication     
from email import encoders         

from config import EMAIL_LOGIN, EMAIL_PASSWORD, PRICELIST_FILENAME

def send_email(receiver, msg_subject, msg_body, attachments):     
	msg = MIMEMultipart()                               
	msg['From']    = EMAIL_LOGIN                          
	msg['To']      = receiver                            
	msg['Subject'] = msg_subject               


	msg.attach(MIMEText(msg_body, 'plain'))                 

	for attach in attachments:
		attach_file_path = attachments[attach]

		with open(attach_file_path, 'rb') as attach_file:
			# payload = MIMEBase('application', 'octate-stream')
			# payload.set_payload((attach_file).read())
			payload = MIMEApplication(attach_file.read())

		# encoders.encode_base64(payload)
		payload.add_header('Content-Disposition', 'attachment', filename=attach)
		msg.attach(payload)

	server = smtplib.SMTP_SSL('smtp.mail.ru', 465)          
	# server.starttls()                                   
	server.login(EMAIL_LOGIN, EMAIL_PASSWORD)                   
	server.send_message(msg)                            
	server.quit()                                       


def main():
	email_text = """Здравствуйте. Во вложении прайс-лист.
		
		С уважением Роман/Александр.

	"""
	attachment = {PRICELIST_FILENAME : f'output/{PRICELIST_FILENAME}'}
	send_email("", 'Прайс-лист', email_text, attachment)


if __name__ == '__main__':
	main()
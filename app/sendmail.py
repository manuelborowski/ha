import smtplib
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("automatisatie.borowski@gmail.com", "AuGoo20ToGle16Matisatie")
 
msg = "Hallo daar"
server.sendmail("automatisatie.borowski@gmail.com", "emmanuel.borowski@gmail.com", msg)
server.quit()

#!/usr/bin/python
import smtplib

server = smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()
server.starttls()
server.ehlo()
server.login("omarleyva93@gmail.com","GOOGLEomar0")
msg = "\nText sent from my Edison!!"
server.sendmail("omarleyva93@gmail.com", "6269759107@messaging.sprintpcs.com", msg)


import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["Subject"] = "Recette"
msg["From"] = "andre@localhost"
msg["To"] = "andre@localhost"
msg.set_content("Voici le fichier demandé")

with open("recette_innocente.pdf", "rb") as f:
    contenu = f.read()

msg.add_attachment(contenu, maintype="application", subtype="pdf", filename="recette_innocente.pdf")

with smtplib.SMTP("localhost", 587) as smtp:
    smtp.send_message(msg)

print("Mail envoyé.")

import smtplib
import getpass
from email.message import EmailMessage

utilisateur = getpass.getuser()
adresse = f"{utilisateur}@localhost"

msg = EmailMessage()
msg["Subject"] = "Recette"
msg["From"] = adresse
msg["To"] = adresse
msg.set_content("Voici le fichier demandé")

with open("recette_innocente.pdf", "rb") as f:
    contenu = f.read()

msg.add_attachment(contenu, maintype="application", subtype="pdf", filename="recette_innocente.pdf")

with smtplib.SMTP("localhost", 587) as smtp:
    smtp.send_message(msg)

print(f"Mail envoyé pour l'utilisateur : {utilisateur}")

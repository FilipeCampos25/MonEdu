def e_mail(destinatario, nome):
    import smtplib
    from email.message import EmailMessage

    try:    
        # Configurações do e-mail
        EMAIL_REMETENTE = "monedosuporte@gmail.com"
        EMAIL_SENHA = "baxv yduf xhva ipog"
        EMAIL_DESTINO = destinatario

        # Criando a mensagem do e-mail
        msg = EmailMessage()
        msg["Subject"] = f"Boas-vindas, {nome}"
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINO
        msg.set_content(f"Olá! \n\nÉ um prazer informá-lo que você foi cadastrado com sucesso em nosso sistema. Se precisar de qualquer assistência, estamos à disposição para ajudar. \n\nAtenciosamente, \nEquipe de Suporte")
    except Exception as e:
        print("O e-mail inserido não existe ou está incorreto. Por favor, verifique e tente novamente.")

    try:
        # Conectando ao servidor SMTP do Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
        print("E-mail enviado com sucesso! O usuário foi notificado sobre o cadastro.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
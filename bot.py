import discord
import pandas as pd
import smtplib
import random
import string
import asyncio

# Importação dos dados de configuração do arquivo 'config.py'
from config import host, username, password, bot_token, planilha_A, planilha_AL, planilha_P

# Configuração das intenções do bot no Discord
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.message_content = True

# Constantes globais
CARGO_ALUNO = "Aluno"
CARGO_PROFESSOR = "Professor"
CARGO_ALGORITMOS = "Cursando Algoritmos"
CARGO_PRETENDENTE = "Pretendente"
CANAL_AUTENTICACAO = "canal-de-autenticação"
TEMPO_LIMITE = 300
TENTATIVAS_MAXIMAS = 3
CODIGO_SEGURANCA_TAMANHO = 6


# Definição da classe do cliente do bot
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emails = {}  # Dicionário para armazenar os e-mails e códigos de segurança
        self.planilha_relatorio = pd.read_excel(planilha_A)  # Leitura da planilha de relatório
        self.planilha_professores = pd.read_excel(planilha_P)  # Leitura da planilha de professores
        self.planilha_algoritmos = pd.read_excel(planilha_AL)  # Leitura da planilha de algoritmos

    def obter_nome_correspondente(self, email):
        # Função para obter o nome correspondente a um e-mail em duas planilhas
        for df in [self.planilha_relatorio, self.planilha_professores]:
            nome_correspondente = df.loc[df['E-mail academico'].astype(str) == email, 'Nome'].values
            if len(nome_correspondente) > 0:
                return nome_correspondente[0]
        return None

    def verificar_email(self, email):
        # Verifica se o e-mail está presente nas planilhas de relatório e professores
        return email in self.planilha_relatorio['E-mail academico'].astype(str).values or email in self.planilha_professores['E-mail'].astype(str).values
   
    @staticmethod
    def tempo_formatado(segundos):
        # Converte o tempo em segundos para o formato "MM minutos e SS segundos"
        minutos = segundos // 60
        segundos = segundos % 60
        return f'{minutos:02d} minutos e {segundos:02d} segundos'

    def enviar_codigo(self, email):
        # Gera um código de segurança e envia por e-mail usando o servidor SMTP do Gmail
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=CODIGO_SEGURANCA_TAMANHO))

        smtp_host = host
        smtp_port = 587
        smtp_user = username
        smtp_password = password

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        subject = 'Código de Segurança'
        message = f'Olá,\n\nSeu código de segurança é: {codigo}\n\nUse esse código para confirmar sua autenticação no servidor.'

        email_message = f'Subject: {subject}\n\n{message}'

        email_message = email_message.encode('utf-8')

        server.sendmail(smtp_user, email, email_message)

        server.quit()

        self.emails[email] = codigo  # Armazena o código de segurança no dicionário de e-mails

        return codigo

    async def on_ready(self):
        # Função chamada quando o bot está pronto e conectado ao Discord
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):

        email = message.content
        member = message.author
        guild = message.guild
        cargo_pretendente = discord.utils.get(guild.roles, name=CARGO_PRETENDENTE)
        cargo_aluno = discord.utils.get(guild.roles, name=CARGO_ALUNO)
        cargo_professor = discord.utils.get(guild.roles, name=CARGO_PROFESSOR)
        cargo_algoritmos = discord.utils.get(guild.roles, name=CARGO_ALGORITMOS)

        # Função chamada quando uma mensagem é enviada para um canal
        if message.author == self.user or message.channel.name != CANAL_AUTENTICACAO:
            return

        print('Message from {0.author}: {0.content}'.format(message))

        if '@' in message.content:
            if email in self.emails:
                # Se o e-mail já foi verificado anteriormente, envia uma mensagem informando
                await message.channel.send('`O email {} já foi verificado anteriormente.`'.format(email))
                await member.ban()
                await message.channel.send(f'O usuário {member.mention} foi banido por tentar verificar um e-mail já verificado.')
            elif self.verificar_email(email):
                # Se o e-mail está presente nas planilhas, envia um código de segurança para o e-mail e inicia a contagem regressiva
                codigo = self.enviar_codigo(email)
                contagem = TEMPO_LIMITE
                msg = await message.channel.send('{}` Email validado. Confirme o código de segurança enviado para o seu email em até {}.`'.format(member.mention, MyClient.tempo_formatado(contagem)))

                while contagem > 0:
                    await asyncio.sleep(1)
                    contagem -= 1
                    await msg.edit(content='{}` Email validado. Confirme o código de segurança enviado para o seu email em até {}.`'.format(member.mention, MyClient.tempo_formatado(contagem)))
                    if cargo_pretendente not in member.roles:
                        break


                if contagem == 0 and cargo_pretendente in member.roles:
                    # Se o usuário não concluir a autenticação dentro do tempo limite, é banido
                    await member.ban()
                    await message.channel.send(f'O usuário {member.mention} foi banido por não concluir a autenticação dentro do tempo limite.')
            else:
                if member.id in self.emails:
                    # Se o usuário já fez tentativas anteriores, incrementa o contador de tentativas
                    self.emails[member.id]['tentativas'] += 1
                    tentativas = self.emails[member.id]['tentativas']
                    await message.channel.send(f'{member.mention} Email inválido. Tentativa {tentativas}/{TENTATIVAS_MAXIMAS}')
                    if tentativas >= TENTATIVAS_MAXIMAS:
                        # Se o usuário exceder o limite de tentativas inválidas, é banido
                        await message.channel.send(f'O usuário {member.mention} foi banido por enviar um e-mail inválido.')
                        await member.ban()
                        del self.emails[member.id]
                else:
                    # Se é a primeira tentativa do usuário, adiciona ao dicionário de e-mails com o contador de tentativas
                    self.emails[member.id] = {'tentativas': 1}
                    await message.channel.send(f'{member.mention} Email inválido. Tentativa 1/{TENTATIVAS_MAXIMAS}')

        if message.content:
            codigo_digitado = message.content
            if len(codigo_digitado) == CODIGO_SEGURANCA_TAMANHO:
                # Verifica se o código digitado está presente nos códigos de verificação armazenados
                if codigo_digitado in self.emails.values():
                    # Obtém o email correspondente ao código digitado
                    email = next(key for key, value in self.emails.items() if value == codigo_digitado)
                    nome_correspondente = self.obter_nome_correspondente(email)
                    await member.add_roles(cargo_aluno)

                    if self.verificar_email(email):
                        # Verifica se o email está presente na planilha de professores
                        if email in self.planilha_professores['E-mail'].astype(str).values:
                            await message.author.add_roles(cargo_professor)
                            await message.author.remove_roles(cargo_aluno)
                            await message.channel.send(f"`Verificação bem-sucedida! Cargo '{CARGO_PROFESSOR}' atribuído a {nome_correspondente}.`")
                        # Verifica se o email está presente na planilha de algoritmos
                        elif email in self.planilha_algoritmos['E-mail academico'].astype(str).values:
                            await message.author.add_roles(cargo_algoritmos)
                            await message.channel.send(f"`Verificação bem-sucedida! Cargos '{CARGO_ALGORITMOS}' e '{CARGO_ALUNO}' atribuídos a {nome_correspondente}.`")
                        else:
                            await message.channel.send(f"`Verificação bem-sucedida! Cargo '{CARGO_ALUNO}' atribuído a {nome_correspondente}.`")

                    # Obtém o nome correspondente ao email e atualiza o apelido do membro
                    if nome_correspondente:
                        await message.author.edit(nick=nome_correspondente)
                        await member.remove_roles(cargo_pretendente)
                else:
                    await message.channel.send("`Código incorreto. Tente novamente.`")


    async def on_member_join(self, member):
        # Função chamada quando um membro entra no servidor
        guild = member.guild
        cargo_pretendente = discord.utils.get(guild.roles, name=CARGO_PRETENDENTE)
        await member.add_roles(cargo_pretendente)

        if guild.system_channel is not None:
            mensagem = '{} `entrou no {}\n\nAntes de ter acesso aos canais do servidor, você deve se autenticar. Digite seu email institucional para autenticação.`'.format(member.mention, guild.name)
            await asyncio.sleep(1)
            await guild.system_channel.send(mensagem)

# Criação de uma instância do cliente e execução do bot
client = MyClient(intents=intents)
client.run(bot_token)
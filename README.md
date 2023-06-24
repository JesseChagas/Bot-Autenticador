# Bot Autenticador

O bot Autenticador é um bot Discord desenvolvido em Python que fornece autenticação de usuários com base em seus e-mails institucionais. O bot verifica se o e-mail fornecido está presente em planilhas de relatório e professores e, em seguida, envia um código de segurança por e-mail para o usuário. O usuário deve digitar o código de segurança no canal de autenticação para concluir o processo de autenticação.

## Configuração

Antes de executar o bot, certifique-se de ter preenchido corretamente o arquivo `config.py` com as informações de configuração necessárias, incluindo o host do servidor SMTP, nome de usuário e senha, token do bot Discord e caminhos para as planilhas.

## Dependências

Certifique-se de ter as seguintes dependências instaladas:

- `discord.py`: Biblioteca para interagir com a API do Discord.
- `pandas`: Biblioteca para manipulação de dados em formato tabular.
- `smtplib`: Biblioteca para envio de e-mails usando protocolo SMTP.

Você pode instalar as dependências usando o seguinte comando:

pip install discord.py pandas

## Utilização

1. Convide o bot Autenticador para o seu servidor Discord.
2. Crie um canal chamado "canal-de-autenticação" (ou ajuste o nome no código, se necessário).
3. Inicie o bot executando o arquivo Python.

O bot estará pronto para autenticar usuários quando eles ingressarem no servidor. Eles serão solicitados a digitar seus e-mails institucionais no canal de autenticação. 
O bot verificará se o e-mail está presente nas planilhas e enviará um código de segurança para o e-mail fornecido. 
O usuário deve digitar o código de segurança no canal de autenticação dentro do tempo limite para concluir a autenticação. 
Se a autenticação for bem-sucedida, o bot atribuirá os cargos apropriados ao usuário com base nas planilhas e atualizará o apelido do usuário com o nome correspondente ao e-mail.

Certifique-se de que o bot tenha as permissões adequadas para banir usuários, adicionar cargos e editar apelidos.

## Notas adicionais

- O bot usa o servidor SMTP para enviar e-mails. Certifique-se de fornecer as informações corretas no arquivo `config.py`.
- Os dados das planilhas são lidos no início da execução do bot e armazenados em memória. Certifique-se de que as planilhas estejam atualizadas antes de iniciar o bot.
- O tempo limite para digitar o código de segurança é de 5 minutos (300 segundos) por padrão, mas pode ser ajustado no código, se necessário.
- O código de segurança gerado é um conjunto de letras maiúsculas e dígitos. O tamanho do código pode ser ajustado no código, se necessário.
- O bot registra suas atividades no console durante a execução.

Certifique-se de revisar o código e ajustá-lo de acordo com suas necessidades antes de implantar o bot Autenticador.

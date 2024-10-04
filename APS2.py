import pymongo
from datetime import datetime, timedelta
import re

uri = "mongodb+srv://leonardofc129:Castilho03@cluster0.ior4b.mongodb.net/Clusters"

while True:
    try:
        client = pymongo.MongoClient(uri)
        client.admin.command('ping')
        print("Conexão com MongoDB estabelecida corretamente")
        break
    except pymongo.errors.ConnectionFailure:
        print("Erro de conexão com o MongoDB. Corrija a URI e tente novamente")
        resposta = input("Gostaria de testar novamente? (s/n): ")
        if resposta.lower() != 's':
            exit()

db = client['biblioteca']
usuarios = db['usuarios']
livros = db['livros']
emprestimos = db['emprestimos']

def validar_cpf(cpf):
    return re.match(r"^\d{11}$", cpf) is not None

def validar_isbn(isbn):
    return re.match(r"^\d{10}|\d{13}$", isbn) is not None

def cadastro_usuarios():
    nome = input("Qual o seu nome? \n")
    email = input("Qual o seu email? \n")
    
    if "@" not in email or "." not in email:
        print("Email inválido. Digite um email válido")
        return
    
    while True:
        data_nasc = input("Quando você nasceu? (Dia/Mês/Ano) \n")
        try:
            data_nasc_obj = datetime.strptime(data_nasc, "%d/%m/%Y").date()
            if data_nasc_obj > datetime.now().date():
                print("A sua data de nascimento não pode ser um dia no futuro")
                continue
            break
        except ValueError:
            print("Data inválida. Use o formato (Dia/Mês/Ano)")
    
    while True:
        documento = input("Qual o número do seu CPF? \n")
        if not validar_cpf(documento):
            print("CPF inválido. Deve ter 11 dígitos")
            continue
        if usuarios.find_one({"documento": documento}):
            print("CPF já cadastrado. Digite um outro CPF")
            continue
        break

    usuario = {
        "nome": nome,
        "email": email,
        "data_nasc": data_nasc_obj,
        "documento": documento
    }
    try:
        usuarios.insert_one(usuario)
        print("Usuário cadastrado com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao cadastrar o usuário: {e}")


def atualizar_usuarios():
    documento = int(input("Qual o número do seu CPF? \n"))

    usuario_existente = usuarios.find_one({"documento": documento})
    if not usuario_existente:
        print("Usuário não encontrado para atualizar")
        return

    nome = input("Qual o novo nome do usuário? \n")
    email = input("Qual o novo email do usuário? \n")
    data_nasc = input("Qual a nova data de nascimento do usuário? \n")

    campos_para_atualizar = {}
    if nome:
        campos_para_atualizar['nome'] = nome
    if email:
        campos_para_atualizar['email'] = email
    if data_nasc:
        campos_para_atualizar['data_nasc'] = data_nasc

    if campos_para_atualizar:
        resultado = usuarios.update_one(
            {"documento": documento},
            {"$set": campos_para_atualizar}
        )
        if resultado.modified_count > 0:
            print(f"Cadastro do usuário com CPF {documento} atualizado com sucesso")
        else:
            print("Nenhuma alteração foi feita no cadastro")
    else:
        print("Nenhum campo foi fornecido para atualização")

def conferir_usuarios():
    procura_usuario = input("Qual o nome do usuário que deseja buscar? \n")
    usuario = usuarios.find_one({"nome": procura_usuario})
    if usuario:
        print(f"Usuário encontrado: {usuario}")
    else:
        print("Usuário não encontrado")

def cadastro_livros():
    titulo = input("Qual o título do livro? \n")
    autor = input("Qual o autor do livro? \n")
    genero = input("Qual o gênero do livro? \n")

    while True:
        try:
            ano_publi = int(input("Qual o ano de publicação do livro? \n"))
            if ano_publi > datetime.now().year:
                print("O ano de publicação não pode ser do futuro")
                continue
            break
        except ValueError:
            print("Ano inválido. Digite um número inteiro")

    while True:
        try:
           isbn = int(input("Qual o ISBN do livro? \n"))
           if not validar_isbn(str(isbn)):
               print("ISBN inválido. Deve ter 10 ou 13 dígitos")
               continue
           break
        except ValueError:
            print("ISBN inválido. Digite um número inteiro")

    while True:
        try:
            qntd_livros = int(input("Quantas cópias do livro estão disponíveis na biblioteca? \n"))
            if qntd_livros < 0:
                print("A quantide de livro não pode ser negativa")
                continue
            break
        except ValueError:
            print("Quantidade inválida. Escreva um número inteiro")

    livro = {
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "ano_publi": ano_publi,
        "isbn": isbn,
        "quantidade": int(qntd_livros)
    }
    try:
        livros.insert_one(livro)
        print("Livro cadastrado com sucesso!")
    except pymongo.errors.OperationFailure as e:
        print(f"Ocorreu um erro ao cadastrar o livro: {e}")

def deletar_livro():
    titulo = input("Qual o título do livro que deseja deletar? \n")

    resultado = livros.delete_one({"titulo": titulo})
    if resultado.deleted_count > 0:
        print(f"Livro {titulo} deletado com sucesso")
    else:
        print(f"Livro {titulo} não foi encontrado para ser deletado")

def atualizar_livros():
    isbn = input("Qual o ISBN do livro que deseja atualizar? \n")

    livro_existente = livros.find_one({"isbn": isbn})
    if not livro_existente:
        print("Livro não encontrado para atualizar")
        return

    titulo = input("Qual o novo título do livro? \n")
    autor = input("Qual o novo autor do livro? \n")
    genero = input("Qual o novo gênero do livro? \n")
    
    while True:
        try:
            ano_publi = int(input("Qual o novo ano de publicação do livro? \n"))
            if ano_publi:
                ano_publi = int(ano_publi)
                if ano_publi > datetime.now().year:
                    print("O ano de publicação não pode ser do futuro")
                    continue
            break
        except ValueError:
            print("Ano inválido. Digite um número inteiro")

    while True:
        try:
            nova_qntd = int(input("Quantas novas cópias do livro estão disponíveis na biblioteca? \n"))
            if nova_qntd:
                nova_qntd = int(nova_qntd)
                if nova_qntd < 0:
                    print("A quantidade não pode ser negativa")
                    continue
            break
        except ValueError:
            print("Quantidade invalida. Escreva um número inteiro")

    campos_para_atualizar = {}
    if titulo:
        campos_para_atualizar['titulo'] = titulo
    if autor:
        campos_para_atualizar['autor'] = autor
    if genero:
        campos_para_atualizar['genero'] = genero
    if ano_publi:
        campos_para_atualizar['ano_publi'] = ano_publi
    if nova_qntd:
        try:
            campos_para_atualizar['quantidade'] = int(nova_qntd)
        except ValueError:
            print("Quantidade inválida. Por gentileza, escreva um número inteiro")
            return

    if campos_para_atualizar:
        resultado = livros.update_one(
            {"isbn": isbn},
            {"$set": campos_para_atualizar}
        )
        if resultado.modified_count > 0:
            print(f"Livro com ISBN {isbn} atualizado com sucesso")
        else:
            print("Nenhuma alteração foi feita no cadastro do livro")

def conferir_livros():
    titulo = input("Qual o livro que deseja buscar? \n")
    livro = livros.find_one({"titulo": titulo})
    if livro:
        print(f"Livro encontrado: {livro}")
    else:
        print("Livro não encontrado")

def todos_livros():
    livros_encontrados = livros.find()
    for livro in livros_encontrados:
        print(livro)

def emprestimo():
    nome = input("Qual o seu nome? \n")
    email = input("Qual o seu email? \n")
    
    while True:
        data_nasc = input("Quando você nasceu? (Dia/Mês/Ano) \n")
        try:
            data_nasc_obj = datetime.strptime(data_nasc, "%d/%m/%Y").date()
            break
        except ValueError:
            print("Data inválida. Use o formato (Dia/Mês/Ano)")
    
    documento = int(input("Qual o número do seu CPF? \n"))
    titulo = input("Qual o nome do livro? \n")
    
    livro = livros.find_one({'titulo': titulo})
    if not livro or livro['quantidade disponivel'] <= 0:
        print("O livro não está disponível para empréstimo")
        return
    
    usuario_existente = usuarios.find_one({'email': email})
    if not usuario_existente:
        usuarios.insert_one({
            "nome": nome,
            "email": email,
            "data_nasc": data_nasc,
            "documento": documento
        })

    data_emprestimo = datetime.now()
    data_devolucao = data_emprestimo + timedelta(days=14)
    emprestimo_info = {
        "usuario_email": email,
        "livro_id": livro['_id'],
        "data_emprestimo": data_emprestimo,
        "data_devolucao": data_devolucao
    }

    emprestimos.insert_one(emprestimo_info)

    livros.update_one({'_id': livro['_id']}, {'$inc': {'quantidade_disponível' -1}})

    print("Empréstimo realizado com sucesso!")

def conferir_emprestimos():
    documento = int(input("Qual o número do seu CPF? \n"))

    emprestimo_existente = emprestimos.find_one({"usuario.documento": documento})
    if emprestimo_existente:
        print("Empréstimo encontrado:")
        print(f"Nome: {emprestimo_existente['usuario']['nome']}")
        print(f"Livro: {emprestimo_existente['livro']['titulo']} por {emprestimo_existente['livro']['autor']}")
        print(f"Data do empréstimo: {emprestimo_existente.get('data_emprestimo', 'Não disponível')}")
    else:
        print("Nenhum empréstimo encontrado com essas informações")

def atualizar_emprestimo():
    documento = int(input("Digite o CPF do empréstimo para atualizar: \n"))

    emprestimo_existente = emprestimos.find_one({"usuario.documento": documento})

    if emprestimo_existente:
        print("Empréstimo encontrado. Atualize os dados (deixe em branco se não quiser atualizar):")

        novo_nome = input(f"Nome ({emprestimo_existente['usuario']['nome']}): ") or emprestimo_existente['usuario']['nome']
        novo_email = input(f"E-mail ({emprestimo_existente['usuario']['email']}): ") or emprestimo_existente['usuario']['email']
        nova_data_nasc = input(f"Data de nascimento ({emprestimo_existente['usuario']['data_nasc']}): ") or emprestimo_existente['usuario']['data_nasc']
        novo_titulo = input(f"Título ({emprestimo_existente['livro']['titulo']}): ") or emprestimo_existente['livro']['titulo']
        novo_autor = input(f"Autor ({emprestimo_existente['livro']['autor']}): ") or emprestimo_existente['livro']['autor']
        novo_genero = input(f"Gênero ({emprestimo_existente['livro']['genero']}): ") or emprestimo_existente['livro']['genero']
        novo_ano_publi = int(input(f"Ano de publicação ({emprestimo_existente['livro']['ano_publi']}): ")) or emprestimo_existente['livro']['ano_publi']
        novo_isbn = int(input(f"ISBN ({emprestimo_existente['livro']['isbn']}): ")) or emprestimo_existente['livro']['isbn']

        emprestimos.update_one(
            {"usuario.documento": documento},
            {"$set": {
                "usuario.nome": novo_nome,
                "usuario.email": novo_email,
                "usuario.data_nasc": nova_data_nasc,
                "livro.titulo": novo_titulo,
                "livro.autor": novo_autor,
                "livro.genero": novo_genero,
                "livro.ano_publi": novo_ano_publi,
                "livro.isbn": novo_isbn
            }}
        )

        print("Empréstimo atualizado com sucesso!")
    else:
        print("Nenhum empréstimo encontrado com esse CPF")

def devolução():
    while True:
        try:
            documento = int(input("Qual o número do seu CPF? \n"))

            if len(str(documento)) != 11:
                print("CPF inválido. Deve ter 11 números")
                continue
            
            emprestimo_existente = emprestimos.find_one({"usuario.documento": documento})
            if not emprestimo_existente:
                print("Nenhum empréstimo encontrado com esse CPF")
                return
            
            titulo = emprestimo_existente['livro']['titulo']
            isbn = emprestimo_existente['livro']['isbn']

            livros.update_one(
                {"isbn": isbn},
                {"$inc": {"quantidade": 1}}
            )

            data_devolucao = datetime.now().strftime("%d/%m/%Y")
            emprestimo.update_one(
                {"usuario_documento": documento},
                {"$set": {"data_devolucao": data_devolucao}}
            )

            print(f"Livro {titulo} devolvido")
            print(f"Data de devolucao: {data_devolucao}")
            break
        except ValueError:
            print("CPF inválido. Deve contter 11 números inteiros")

def menu():
    while True:
        print("\nMenu Biblioteca")
        print("1 - Cadastrar usuário")
        print("2 - Atualizar usuário")
        print("3 - Conferir usuário")
        print("4 - Cadastrar livro")
        print("5 - Atualizar livro")
        print("6 - Deletar livro")
        print("7 - Conferir livro pelo título")
        print("8 - Ver todos os livros")
        print("9 - Emprestar livro")
        print("10 - Conferir empréstimos")
        print("11 - Atualizar empréstimos")
        print("12 - Devolver livro")
        print("13 - Sair")

        escolha = input("Escolha uma das opções: ")

        if escolha == '1':
            cadastro_usuarios()
        elif escolha == '2':
            atualizar_usuarios()
        elif escolha == '3':
            conferir_usuarios()
        elif escolha == '4':
            cadastro_livros()
        elif escolha == '5':
            atualizar_livros()
        elif escolha == '6':
            deletar_livro()
        elif escolha == '7':
            conferir_livros()
        elif escolha == '8':
            todos_livros()
        elif escolha == '9':
            emprestimo()
        elif escolha == '10':
            conferir_emprestimos()
        elif escolha == '11':
            atualizar_emprestimo()
        elif escolha == '12':
            devolução()
        elif escolha == '13':
            print("Saindo")
            break
        else:
            print("Opção inválida. Tente novamente.")

        input("Aperte Enter para voltar ao menu")

menu()

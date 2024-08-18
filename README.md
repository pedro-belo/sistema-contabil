# Sobre

## Descrição

EquiBook é um projeto de estudo para fixar conceitos aprendidos sobre contabilidade introdutória. Seu nome refere-se a junção das palavras Livro e Equilíbrio. O livro consiste em uma série de transações realizadas ao longo de determinado período e que sempre se mantém em equilíbrio a partir de lançamentos a crédito/débito.

## Funcionalidades

### Login e Cadastro Básico:

A autenticação é feita por meio de login com usuário e senha.

O cadastro de um novo usuário requer as credenciais e a seleção da moeda base que será utilizada no sistema. Moedas disponíveis: BRL, USD, EUR, JPY, GBP, CNY.

### Setup Inicial de Período Contábil:

Configuração do período contábil, permitindo definir datas de início e fim para o ciclo contábil. Isso garante que todas as transações, lançamentos e apurações estejam associadas ao período correto.

### Estruturação de Contas:

Estruturação e organização do plano de contas, onde são definidos os grupos e subgrupos contábeis, como ativos, passivos, receitas e despesas. Essa planificação serve como base para o registro adequado das transações financeiras.

### Registro de Transações Débito/Crédito:

Lançamento de transações contábeis no sistema, registrando os movimentos de débito e crédito para manter o balanço patrimonial atualizado. Essa função assegura a dupla entrada, garantindo que cada transação afete de maneira correta as contas envolvidas.

### Apuração de Resultado

Cálculo do resultado do exercício (lucro ou prejuízo) com base nas receitas e despesas registradas. Esse processo envolve a consolidação das contas de resultado e a preparação para o encerramento do período.

### Encerramento de Período Contábil

Procedimento de fechamento do período contábil, onde as contas de resultado são zeradas e transferidas para o patrimônio líquido. Esse encerramento permite iniciar um novo ciclo contábil com as contas de resultado limpas.

### Balancete Simplificado

Geração de um balancete contábil resumido, apresentando a posição financeira da empresa em determinado período. Este balancete exibe os saldos das principais contas, facilitando uma visão geral rápida da saúde financeira.

### Visualização de Valores em Diferentes Moedas

Conversão e exibição de valores financeiros em diferentes moedas, com base nas taxas de câmbio.

#### Observação

Devido à utilização de estruturas de dados como árvores e listas encadeadas nos modelos, a representação das contas planificadas (em formato de árvore) e das transações de débito/crédito (em formato de lista encadeada) é mantida em cache utilizando Redis. Isso é feito para evitar problemas de performance, já que essas operações podem se tornar custosas em termos de tempo e recursos quando processadas diretamente do banco de dados a cada requisição.

# Setup

## Pré-requisitos

A utilização do projeto pode ser feita executando a aplicação diretamente ou através de containers.

Em ambos os casos é necessário ter o python instalado em sua máquina. A versão do python utilizada no projeto é a 3.10. Más caso o valor seja alterado no futuro você pode conferir essa informação no arquivo **pyproject.toml**. Caso não tenha essa versão do python, considere o uso de ferramentas como o pyenv para gerenciar diferentes versões do python no seu sistema operacional.

Também é recomendado, mas não obrigatório, o utilitário make.

## Instalação

**1. Faça o clone deste repositório**

    git clone https://github.com/pedro-belo/sistema-contabil.git

**2**. Após o download e descompactação vá para a raiz do projeto. (onde existe um arquivo chamado manage.py)

    cd sistema-contabil

**3. Inicie o ambiente virtual usando python ou poetry**

    python -m venv .venv

ou

    poetry shell

**4. Ative o ambiente criado usando python ou poetry**

    source .venv/bin/activate

ou

    poetry install

**4. Instalação de dependências do python**

    pip install -r requirements.txt

ou

    poetry install

**5. Instalação de dependências para gerenciamento dos arquivos estáticos**

    # Considerando que você está na raiz do projeto
    cd equibook/core/static/
    npm install
    npm run build

**6. Volte para o diretório raiz do projeto**

    # Considerando que você está em equibook/core/static/
    cd -

**7. Configurações de variáveis de ambiente**

    cp .default.env .env -i

**8. Aplicação de migrações**

    python manage.py migrate

## Execução

**1. Inicie o servidor**

    python manage.py runserver

**2. Acesse o endereço da sua interface de loopback**

    http://127.0.0.1:8000

ou

    http://localhost:8000

## Uso

O uso será demonstrado através do exemplo a seguir, retirado do livro "Contabilidade Introdutória - Livro de Exercícios (Sérgio de Iudícibus e Eliseu Martins)"

**EXERCÍCIO 3.1**
A seguir estão relacionadas as operações realizadas pela sociedade de prestação de serviços Remendão S.A., em
janeiro/X2 (em $):

**1** investimento inicial de capital no valor total de $ 10.000 em dinheiro;

**2** compra à vista de móveis e utensílios, na importância de $ 2.000;

**3** compra de peças para reparos, nas seguintes condições: $ 500 à vista e $ 1.000 a prazo;

**4** venda a prazo de $ 500 de peças para reparos, pelo preço de custo;

**5** compra de um veículo, a prazo, por $ 600, mediante a emissão de uma nota promissória;

**6** pagamento de 50% da dívida relativa à compra de peças para reparos;

**7** investimento adicional dos sócios, aumentando o capital em mais $ 5.000, sendo $ 2.500 em dinheiro e $
2.500 em peças para reparos;

**8** venda à vista de $ 200 em peças para reparos, pelo preço de custo;

**9** recebimento do valor da venda a prazo referente ao item 4;

**10**. obtenção de um empréstimo, depositado pelo banco na conta-corrente da empresa, no último dia do mês de
janeiro/X2, no valor de $ 5.000, mediante a emissão de uma nota promissória;

Resolução em:
[Exemplo de Uso](https://github.com/pedro-belo/sistema-contabil/tree/main/example)

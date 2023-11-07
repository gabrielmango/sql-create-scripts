print('-' * 50)
print('SQL script creation of table in database:')
print('-' * 50)
print()

def input_info(mensage, name, _string='', max_length=30):
    ''' Prompts the user for text input with a maximum length and returns the input if it's valid. '''
    _string = input(mensage)
    if name == 'comment' or name == 'constraint':
        max_length = 1000
    if name == 'table':
        max_length = 25
    while True:
        if len(_string) <= max_length:
            return _string
        print(f"Sorry, the {name} must have a maximum of {max_length} characters.\n")
        _string = input(f"Please enter a {name} (up to {max_length} characters): ").lower()


# Getting the project schema
project_schema = input_info('Enter the project schema name: ', 'schema')

# Getting the table comment and check table name length
main_table_name = input_info('Enter the table name: ', 'table')

# Getting the table name and check table name length
main_table_comment = input_info('Enter the table comment: ', 'comment')

# Getting the sequence
abbreviation = [letter[0] for letter in main_table_name[3:].split('_')]
main_table_sequence = f'sq_{main_table_name[3:].replace("_", "")}_coseq' + ''.join(abbreviation)

# Checking the lenght of sequence
while True:
    if len(main_table_sequence) <= 30:
        break
    print(f"Sorry, the sequence ({main_table_sequence}) must have a maximum of 30 characters. It has {len(main_table_sequence)}.\n")
    main_table_sequence = input_info("Please enter a sequence (up to 30 characters): ")

# Getting information from table columns 
columns = []
while True:
    columns.append({
        # Getting the column name
        'name': input_info('Enter the column name: ', 'column'),

        # Getting the column type
        'type': input_info('Enter the column type: ', 'column'),

        # Getting the column mandatory
        'mandatory': input_info('Is the column NULL or NOT NULL? ', 'column'),

        # Gettinh the column comment
        'comment': input_info('Enter the column comment: ', 'comment')
    })

    # Check add another column info
    answer = input('Do you want to add another column? (y/n) ')

    if answer.lower() == 'n':
        break

# Create de first part of the SQL Script
sql_script = f'''
---------------------------------------
-- Tabela {main_table_name.upper()}
---------------------------------------
---- DROP TABLE    IF EXISTS {project_schema}.{main_table_name} CASCADE;
---- DROP SEQUENCE IF EXISTS {project_schema}.{main_table_sequence};

CREATE SEQUENCE IF NOT EXISTS {project_schema}.{main_table_sequence} INCREMENT 1 START 1;


CREATE TABLE IF NOT EXISTS {project_schema}.{main_table_name} (
  co_seq_{main_table_name[3:]}  BIGINT  NOT NULL DEFAULT nextval('{project_schema}.{main_table_sequence}'),
'''

# Add columns to SQL Script
for index, column in enumerate(columns):
    if index == len(columns) - 1:
        sql_script += f'  {column["name"]}    {column["type"]}    {column["mandatory"]},'
    else:
        sql_script += f'  {column["name"]}    {column["type"]}    {column["mandatory"]}, \n'

# Add default columns
sql_script += '''
  sg_projeto_modificador          VARCHAR(100)      NULL,
  sg_acao_modificadora            VARCHAR(100)      NULL,
  no_end_point_modificador        VARCHAR(255)      NULL,
  st_ativo                        BOOLEAN       NOT NULL,
  dh_criacao                      TIMESTAMP WITHOUT TIME ZONE NULL,
  dh_alteracao                    TIMESTAMP WITHOUT TIME ZONE NULL,
  tp_operacao                     VARCHAR(255)  NOT NULL,
  nu_versao                       NUMERIC(10)   NOT NULL,
  co_uuid                         VARCHAR(255)  NOT NULL,
  co_uuid_1                       VARCHAR(255)      NULL, \n'''

# Checking the lenght of primary key
primary_key = 'pk_' + main_table_name[3:].replace("_", "")

while True:
    if len(primary_key) <= 30:
        break
    print(f"Sorry, the sequence ({primary_key}) must have a maximum of 30 characters. It has {len(primary_key)}.\n")
    primary_key = input_info("Please enter a primary key (up to 30 characters): ")

# Add the Constraint Primary Key to SQL Script
sql_script += f'  CONSTRAINT {primary_key} PRIMARY KEY (co_seq_{main_table_name[3:]})'

# Getting more constraints to the table
constraints = []
while True:
    # Check add another constraint info
    is_constraint = input('Do you want to add any more constraints? (y/n) ')

    if is_constraint.lower() == 'n':
        break

    constraints.append({
        # Getting the constraint name
        'name': input_info('Enter the constraint name: ', 'constraint name'),

        # Getting the constraint description
        'description': input_info('Enter the constraint description: ', 'constraint description'),
    })

# Add constraints to SQL Script
sql_script += '\n'
if len(constraints) > 0:
    for index, constraint in enumerate(constraints):
        if index == 1:
            sql_script += ', \n'
        if index == len(constraints) - 1:
            sql_script += f'  CONSTRAINT {constraint["name"]} {constraint["description"]}'
        else:
            sql_script += f'  CONSTRAINT {constraint["name"]} {constraint["description"]},'
    sql_script += '\n);'


# Create the table comment to SQL Script
sql_script += f"\n\n\nCOMMENT ON TABLE {project_schema}.{main_table_name} IS '{main_table_comment}';\n"

# Add the first column comment to SQL Script
sql_script += f"COMMENT ON COLUMN {project_schema}.{main_table_name}.co_seq_{main_table_name[3:]} IS 'Chave primaria sequencial da tabela que eh gerada pela sequence {main_table_sequence}.';\n"

# Add columns comments to SQL Script
for index, column in enumerate(columns):
    if index == len(constraints) - 1:
        sql_script += f"COMMENT ON COLUMN {project_schema}.{main_table_name}.{column['name']} IS '{column['comment']}';"
    else:
        sql_script += f"COMMENT ON COLUMN {project_schema}.{main_table_name}.{column['name']} IS '{column['comment']}';\n"

sql_script += f'''
COMMENT ON COLUMN {project_schema}.{main_table_name}.sg_projeto_modificador         IS 'Sigla do projeto que iniciou o processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.sg_acao_modificadora           IS 'Sigla da acao do processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.no_end_point_modificador       IS 'Nome do end point que iniciou o processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.st_ativo                       IS 'Estado da ativacao do registro.  TRUE = Ativo ou FALSE = Inativo.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.dh_criacao                     IS 'Data da criacao do registro.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.dh_alteracao                   IS 'Data da ultima alteracao do registro.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.tp_operacao                    IS 'Tipo de operacao realizada no registro. Por exemplo: CREATE, READ, UPDATE, DELETE.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.nu_versao                      IS 'Numero da versao do registro.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.co_uuid                        IS 'Identificador unico universal (do ingles universally unique identifier - UUID). Na tabela cada registro tem seu UUID com identificacao unica.';
COMMENT ON COLUMN {project_schema}.{main_table_name}.co_uuid_1                      IS 'UUID do usuario que realizou a alteracao no registo.'';
\n\n\n
'''


# Create the history table
# Getting the history table name
history_table_name = main_table_name.replace('tb', 'th') + '_hist'

# Getting the sequence
abbreviation = [letter[0] for letter in history_table_name[3:].split('_')]
history_table_sequence = f'sq_{history_table_name[3:].replace("_", "")}_coseq' + ''.join(abbreviation)

# Cheking the lenght of history sequence
while True:
    if len(main_table_sequence) <= 30:
        break
    print(f"Sorry, the history sequence ({history_table_sequence}) must have a maximum of 30 characters. It has {len(history_table_sequence)}.\n")
    history_table_sequence = input_info("Please enter a sequence (up to 30 characters): ")

# Create de second part of the SQL Script
sql_script += f'''
---------------------------------------
-- Tabela {history_table_name.upper()}
---------------------------------------
---- DROP TABLE    IF EXISTS {project_schema}.{history_table_name} CASCADE;
---- DROP SEQUENCE IF EXISTS {project_schema}.{history_table_sequence};

CREATE SEQUENCE IF NOT EXISTS {project_schema}.{history_table_sequence} INCREMENT 1 START 1;


CREATE TABLE IF NOT EXISTS distribuicao.th_juizado_hist (
  co_seq_{history_table_name[3:]}   BIGINT  NOT NULL DEFAULT nextval('{project_schema}.{history_table_sequence}'),
  co_seq_{main_table_name[3:]}  BIGINT  NOT NULL,
'''

# Add columns to SQL Script
for index, column in enumerate(columns):
    if index == len(columns) - 1:
        sql_script += f'  {column["name"]}    {column["type"]}    {column["mandatory"]},'
    else:
        sql_script += f'  {column["name"]}    {column["type"]}    {column["mandatory"]}, \n'

# Add default columns
sql_script += '''
  sg_projeto_modificador          VARCHAR(100)      NULL,
  sg_acao_modificadora            VARCHAR(100)      NULL,
  no_end_point_modificador        VARCHAR(255)      NULL,
  st_ativo                        BOOLEAN       NOT NULL,
  dh_criacao                      TIMESTAMP WITHOUT TIME ZONE NULL,
  dh_alteracao                    TIMESTAMP WITHOUT TIME ZONE NULL,
  tp_operacao                     VARCHAR(255)  NOT NULL,
  nu_versao                       NUMERIC(10)   NOT NULL,
  co_uuid                         VARCHAR(255)  NOT NULL,
  co_uuid_1                       VARCHAR(255)      NULL,
  dh_inicio_hist                  TIMESTAMP WITHOUT TIME ZONE NULL,
  dh_fim_hist                     TIMESTAMP WITHOUT TIME ZONE NULL,
'''

# Checking the lenght of history primary key
history_primary_key = 'pk_' + history_table_name[3:].replace("_", "")

while True:
    if len(history_primary_key) <= 30:
        break
    print(f"Sorry, the sequence ({history_primary_key}) must have a maximum of 30 characters. It has {len(history_primary_key)}.\n")
    history_primary_key = input_info("Please enter a history primary key (up to 30 characters): ")

# Add the Constraint Primary Key to SQL Script
sql_script += f'  CONSTRAINT {history_primary_key} PRIMARY KEY (co_seq_{history_table_name[3:]}) \n'
sql_script += ');\n'

# Create the table comment to SQL Script
sql_script += f"\n\nCOMMENT ON TABLE {project_schema}.{history_table_name} IS 'Tabela de historico de alteracoes realizadas nos registros da tabela {main_table_name}.';\n"

# Add the first column comment to SQL Script
sql_script += f"COMMENT ON COLUMN {project_schema}.{history_table_name}.co_seq_{history_table_name[3:]} IS 'Chave primaria sequencial da tabela que eh gerada pela sequence {main_table_sequence}.';\n"

# Add the second column comment to SQL Script
sql_script += f"COMMENT ON COLUMN {project_schema}.{history_table_name}.co_seq_{main_table_name[3:]} IS 'Codigo {main_table_name[3:]}. Vem da tabela {main_table_name}.';\n"

# Add columns comments to SQL Script
for index, column in enumerate(columns):
    if index == len(constraints) - 1:
        sql_script += f"COMMENT ON COLUMN {project_schema}.{history_table_name}.{column['name']} IS '{column['comment']}';"
    else:
        sql_script += f"COMMENT ON COLUMN {project_schema}.{history_table_name}.{column['name']} IS '{column['comment']}';\n"

sql_script += f'''
COMMENT ON COLUMN {project_schema}.{history_table_name}.sg_projeto_modificador         IS 'Sigla do projeto que iniciou o processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.sg_acao_modificadora           IS 'Sigla da acao do processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.no_end_point_modificador       IS 'Nome do end point que iniciou o processo modificador do dado.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.st_ativo                       IS 'Estado da ativacao do registro.  TRUE = Ativo ou FALSE = Inativo.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_criacao                     IS 'Data da criacao do registro.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_alteracao                   IS 'Data da ultima alteracao do registro.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.tp_operacao                    IS 'Tipo de operacao realizada no registro. Por exemplo: CREATE, READ, UPDATE, DELETE.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.nu_versao                      IS 'Numero da versao do registro.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.co_uuid                        IS 'Identificador unico universal (do ingles universally unique identifier - UUID). Na tabela cada registro tem seu UUID com identificacao unica.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.co_uuid_1                      IS 'UUID do usuario que realizou a alteracao no registo.'';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_inicio_hist                 IS 'Data que o registro foi incluido na tabela de historico';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_fim_hist                    IS 'Data que o registro foi inativado na tabela de historico, porque um novo registro foi incluido na Tabela. Indica que uma nova alteracao foi realizada na tabela origem.';
'''

# Create name of the SQL Script
sql_script_name = f'V__CRIATE_TABELA_{main_table_name.upper()}.sql'

# Create de file .sql
with open(sql_script_name, 'w') as file:
    file.write(sql_script)
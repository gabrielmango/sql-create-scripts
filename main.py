print('-' * 50)
print('SQL script creation of table in database:')
print('-' * 50)
print()

def input_info(mgs, max_length=30):
    text = input(mgs)
    valid_name(text, max_length)
    return text


def valid_name(text, max_length=30):
    while True:
        if len(text) <= max_length:
            break
        print(f"Sorry, the sequence ({text}) must have a maximum of 30 characters. It has {len(text)} characters.\n")
        text = input_info("Please enter a sequence (up to 30 characters): ")


project_schema = input_info('Enter the project schema name: ')
main_table_name = input_info('Enter the table name: ')
main_table_comment = input_info('Enter the table comment: ', 255)

abbreviation = [letter[0] for letter in main_table_name[3:].split('_')]
main_table_sequence = f'sq_{main_table_name[3:].replace("_", "")}_coseq' + ''.join(abbreviation)
valid_name(main_table_sequence)


# Getting information from table columns
columns = []
while True:
    columns.append({
        # Getting the column name
        'name': input_info('Enter the column name: '),

        # Getting the column type
        'type': input_info('Enter the column type: '),

        # Getting the column mandatory
        'mandatory': input_info('Is the column NULL or NOT NULL? '),

        # Gettinh the column comment
        'comment': input_info('Enter the column comment: ', 255)
    })

    # Check add another column info
    answer = input('Do you want to add another column? (y/n) ')

    if answer.lower() == 'n':
        break

# Create de first part of the SQL Script
sql_script = f'''
---------------------------------------
-- TABELA {main_table_name.upper()}
---------------------------------------
-- DROP TABLE    IF EXISTS {project_schema}.{main_table_name} CASCADE;
-- DROP SEQUENCE IF EXISTS {project_schema}.{main_table_sequence};

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
valid_name(primary_key)


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
else:
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
        sql_script += f"\nCOMMENT ON COLUMN {project_schema}.{main_table_name}.{column['name']} IS '{column['comment']}';"

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
COMMENT ON COLUMN {project_schema}.{main_table_name}.co_uuid_1                      IS 'UUID do usuario que realizou a alteracao no registo.';
\n\n\n
'''


# Create the history table
# Getting the history table name
history_table_name = main_table_name.replace('tb', 'th') + '_hist'

# Getting the sequence
abbreviation = [letter[0] for letter in history_table_name[3:].split('_')]
history_table_sequence = f'sq_{history_table_name[3:].replace("_", "")}_coseq' + ''.join(abbreviation)
valid_name(history_table_sequence)


# Create de second part of the SQL Script
sql_script += f'''
---------------------------------------
-- TABELA {history_table_name.upper()}
---------------------------------------
-- DROP TABLE    IF EXISTS {project_schema}.{history_table_name} CASCADE;
-- DROP SEQUENCE IF EXISTS {project_schema}.{history_table_sequence};

CREATE SEQUENCE IF NOT EXISTS {project_schema}.{history_table_sequence} INCREMENT 1 START 1;


CREATE TABLE IF NOT EXISTS {project_schema}.{history_table_name} (
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
valid_name(history_primary_key)


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
COMMENT ON COLUMN {project_schema}.{history_table_name}.co_uuid_1                      IS 'UUID do usuario que realizou a alteracao no registo.';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_inicio_hist                 IS 'Data que o registro foi incluido na tabela de historico';
COMMENT ON COLUMN {project_schema}.{history_table_name}.dh_fim_hist                    IS 'Data que o registro foi inativado na tabela de historico, porque um novo registro foi incluido na Tabela. Indica que uma nova alteracao foi realizada na tabela origem.';
'''

sql_script += '\n'

# Create trigger
trigger_name = f'traiu_{main_table_name[3:].replace("_", "")}'
valid_name(trigger_name)

trigger_function_name = f'fc_log_{main_table_name[3:].replace("_", "")}'
valid_name(trigger_function_name)


sql_script += f'''
-----------------------------------------------
-- TRIGGER DA TABELA {main_table_name.upper()}
-----------------------------------------------
-- DROP FUNCTION IF EXISTS {trigger_function_name};
-- DROP TRIGGER IF EXISTS {trigger_name} ON {main_table_name};

CREATE OR REPLACE FUNCTION {trigger_function_name}()
RETURNS trigger AS
$BODY$
	begin
		INSERT INTO {project_schema}.{history_table_name}(
										co_seq_{main_table_name[3:]},
'''

for column in columns:
    sql_script += f'										{column["name"]},'


sql_script += f'''
										sg_projeto_modificador,
                                        sg_acao_modificadora,
                                        no_end_point_modificador,
                                        st_ativo,
                                        dh_criacao,
                                        dh_alteracao,
                                        tp_operacao,
                                        nu_versao,
                                        co_uuid,
                                        co_uuid_1,
                                        dh_inicio_hist)
								values(
										new.co_seq_{main_table_name[3:]}, 
'''

for column in columns:
    sql_script += f'										new.{column["name"]},'

sql_script += f'''
										new.sg_projeto_modificador,
                                        new.sg_acao_modificadora,
                                        new.no_end_point_modificador,
                                        new.st_ativo,
                                        new.dh_criacao,
                                        new.dh_alteracao,
                                        new.tp_operacao,
                                        new.nu_versao,
                                        new.co_uuid,
                                        new.co_uuid_1,
                                        now());
	RETURN NEW;
	END;
$BODY$
LANGUAGE plpgsql;
\n\n
'''

sql_script += f'''
CREATE TRIGGER {trigger_name}
AFTER INSERT OR UPDATE ON {project_schema}.{main_table_name} 
FOR EACH ROW
EXECUTE PROCEDURE {trigger_function_name}();
\n\n
'''




# Create name of the SQL Script
sql_script_name = f'V__CRIATE_TABELA_{main_table_name.upper()}.sql'





# Create de file .sql
with open(sql_script_name, 'w') as file:
    file.write(sql_script)
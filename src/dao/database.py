import psycopg2

con, cur = None, None

def connect():
    global cur, con

    con = psycopg2.connect(
        host="localhost",
        database="easy_finance_controller_dev",
        # database="easy_finance_controller_prod",
        user="postgres",
        password="admin"
    )
    cur = con.cursor()

def disconnect():
    global cur, con
    cur.close()
    con.close()

def get_movement_types(cod_mov=''):
    """
    Returns the description of a movement
    """
    connect()
    if cod_mov == '':
        hide_where = '--'
    else:
        hide_where = ''

    query = f"""SELECT
    BDCODMOVIMENTACAO||' - '||BDDESCMOVIMENTACAO
FROM 
    TIPOMOVIMENTACAO
{hide_where}WHERE
    {hide_where}BDCODMOVIMENTACAO = {cod_mov}
ORDER BY BDCODMOVIMENTACAO;"""
    
    cur.execute(query)
    res = cur.fetchall()
    res = [list(i)[0] for i in res]

    disconnect()

    return res

def get_categories(table=False):
    """
    Returns the description of financial categories
    """
    connect()
    if table:
        query = f"""SELECT 
        BDCODCAT,
        BDDESCCAT,
        REPLACE(TO_CHAR(EXTRACT(DAY FROM BDDATACADASTRO), 'FM00') || '/' ||
        TO_CHAR(EXTRACT(MONTH FROM BDDATACADASTRO), 'FM00') || '/' ||
        TO_CHAR(EXTRACT(YEAR FROM BDDATACADASTRO), '0000'),' ','') AS BDDATACADASTRO
    FROM
        CATEGORIA_MOVIMENTACAO
    WHERE
        BDSTATUS IS TRUE
    ORDER BY 
        BDCODCAT;"""
        cur.execute(query)
        res = cur.fetchall()
        res = [list(i) for i in res]

    else:
        query = f"""SELECT 
        BDCODCAT||' - '||BDDESCCAT
    FROM
        CATEGORIA_MOVIMENTACAO
    WHERE
        BDSTATUS IS TRUE
    ORDER BY 
        BDCODCAT;"""
    
        cur.execute(query)
        res = cur.fetchall()
        res = [list(i)[0] for i in res]

    disconnect()

    return res

def get_participants():
    """
    Returns a list of registered participants
    """
    connect()

    query = f"""SELECT 
	BDCODTER||' - '||BDAPELIDOTER||' - '||BDCNPJTER
FROM 
	TERCEIRO
--WHERE
--	BDREFTER = (SELECT MAX(T1.BDREFTER) FROM TERCEIRO T1 WHERE T1.BDCODTER = BDCODTER);"""
    
    cur.execute(query)
    res = cur.fetchall()
    res = [list(i)[0] for i in res]

    disconnect()

    return res

def get_all_participants():
    """
    Returns a list of all participants
    """
    connect()

    query = f"""
SELECT
	BDCODTER||' - '||BDNOMETER AS NOMETER,
	BDAPELIDOTER,
	BDCNPJTER,
	BDREFTER
FROM 
	TERCEIRO;"""
    
    cur.execute(query)
    res = cur.fetchall()
    res = [list(i) for i in res]

    disconnect()

    return res

def launch_financial_movement(bdreflan, bddatatrans, bddatalan, bdhoralan, bdcodcat, bddescmov, bdvlr, bdvlrdesc, bdcodter, bdcodmov):
    """
    Lauches the movement on table 'movimentacao_financeira'
    """
    connect()

    query = """
        INSERT INTO public.movimentacao_financeira(
            bdreflan, bddatatransacao, bddatalan, bdhoralan, bdcodcat, 
            bddescmov, bdvlrtransacao, bdvlrdesconto, bdcodter, bdcodmovimentacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    try:
        cur.execute(query, (bdreflan, bddatatrans, bddatalan, bdhoralan, bdcodcat, bddescmov, bdvlr, bdvlrdesc, bdcodter, bdcodmov))
        con.commit() 
        disconnect()  
        return True
    except Exception as e:
        disconnect()  
        print(e)
        return False

def get_financial_movements(bdreflan_start, bdreflan_end, bdcodmovimentacao, bdcodcat, bdcodter):
    """
    Lauches the movement on table 'movimentacao_financeira'
    """
    connect()

    query = f"""
SELECT 
    FIN.BDCODTRANSACAO AS CODIGO,
    LPAD(TO_CHAR(EXTRACT(DAY FROM FIN.BDDATATRANSACAO), 'FM00'), 2, '0') || '/' ||
    LPAD(TO_CHAR(EXTRACT(MONTH FROM FIN.BDDATATRANSACAO), 'FM00'), 2, '0') || '/' ||
    EXTRACT(YEAR FROM FIN.BDDATATRANSACAO) AS DATA_TRANSACAO,
    CAT.BDDESCCAT AS CATEGORIA,
    TER.BDAPELIDOTER AS TERCEIRO,
    TIP.BDDESCMOVIMENTACAO AS MOVIMENTACAO,
    FIN.BDVLRTRANSACAO AS VALOR
FROM
    MOVIMENTACAO_FINANCEIRA FIN
LEFT JOIN
    CATEGORIA_MOVIMENTACAO CAT ON CAT.BDCODCAT = FIN.BDCODCAT
LEFT JOIN
    TERCEIRO TER ON TER.BDCODTER = FIN.BDCODTER	
LEFT JOIN
    TIPOMOVIMENTACAO TIP ON TIP.BDCODMOVIMENTACAO = FIN.BDCODMOVIMENTACAO
WHERE
	FIN.BDREFLAN BETWEEN %s AND %s
	{'--' if str(bdcodmovimentacao).lower() == 'todos' else ''}AND FIN.BDCODMOVIMENTACAO = %s
	{'--' if str(bdcodcat) == '0' else ''}AND FIN.BDCODCAT = %s
	{'--' if str(bdcodter) == '0' else ''}AND FIN.BDCODTER = %s
ORDER BY
    FIN.BDDATATRANSACAO,
    FIN.BDCODTRANSACAO;
    """

    try:
        cur.execute(query, (bdreflan_start, bdreflan_end, bdcodmovimentacao, bdcodcat, bdcodter))
        res = cur.fetchall()
        res = [list(i) for i in res]
        disconnect()  
        return res
    except Exception as e:
        disconnect()  
        print(e)
        return False

def register_participant(bdnometer, bdapelidoter, bdcnpjter, bdrefter):
    """
    Register a new participant
    """
    connect()

    query = """
INSERT INTO public.terceiro(
	bdnometer, bdapelidoter, bdcnpjter, bdrefter)
	VALUES (%s, %s, %s, %s);
    """

    try:
        cur.execute(query, (bdnometer, bdapelidoter, bdcnpjter, bdrefter))
        con.commit() 
        disconnect()  
        return True
    except Exception as e:
        disconnect()  
        print(e)
        return False

def register_category(bddesccat, bddatacadastro, bdstatus):
    """
    Register a new category on database
    """

    connect()
    query = """
INSERT INTO public.categoria_movimentacao(
	bddesccat, bddatacadastro, bdstatus)
	VALUES (%s, %s, %s);
"""
    try:
        cur.execute(query, (bddesccat, bddatacadastro, bdstatus))
        con.commit() 
        disconnect()  
        return True
    except Exception as e:
        disconnect()  
        print(e)
        return False

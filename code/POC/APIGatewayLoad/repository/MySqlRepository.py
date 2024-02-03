import config
import mysql
import mysql.connector
import pandas
import domain.Uri
import domain.Correlation
import domain.RepeatedAttributes
import dateutil
import datetime
import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class MySqlRepository:

    def __init__(self):
        pass

    # Verifica se os campos requeridos da Uri estão todos preenchidos
    @staticmethod
    def check_uri_required(obj: domain.Uri.Uri) -> bool:
        if (obj.get_uri() == "" or pandas.isnull(obj.get_uri())) or (
                pandas.isnull(obj.get_client_id()) or obj.get_client_id() == "") or (
                pandas.isnull(obj.get_request_timestamp()) or obj.get_request_timestamp() == ""):
            return False
        else:
            return True

    @staticmethod
    def create_uri(obj: domain.Uri.Uri):
        if (obj.get_uri() == "" or pandas.isnull(obj.get_uri())) or (
                pandas.isnull(obj.get_client_id()) or obj.get_client_id() == "") or (
                pandas.isnull(obj.get_request_timestamp()) or obj.get_request_timestamp() == ""):
            return None
        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )

        cursor = mydb.cursor()
        try:

            dml = "INSERT INTO EA_Discovery.uri (uri, clientId, requestTimeStamp) VALUES (%s, %s, %s)"
            # data = dateutil.parser(request_timestamp)
            data_obj = datetime.strptime(obj.get_request_timestamp(), '%Y/%m/%d %H:%M:%S %z')
            vals = (obj.get_uri(), obj.get_client_id(), data_obj)
            cursor.execute(dml, vals)
            mydb.commit()

        except mysql.connector.errors.InterfaceError as ie:
            if ie.msg == 'No result set to fetch from.':
                # no problem, we were just at the end of the result set
                pass
            else:
                raise
        except mydb.connector.Error as e:
            print("Error reading data from MySQL table", e)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
        finally:
            if mydb.is_connected():
                mydb.close()
                cursor.close()

    @staticmethod
    def find_uri(obj: domain.Uri.Uri) -> domain.Uri.Uri:
        # busca se existe registro na tabela uri, basicamente uma mesma uri chamada por um clint_id no mesmo momento

        if (obj.get_uri() == "" or pandas.isnull(obj.get_uri())) or (
                pandas.isnull(obj.get_client_id()) or obj.get_client_id() == "") or (
                pandas.isnull(obj.get_request_timestamp()) or obj.get_request_timestamp() == ""):
            return None

        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor()
        try:

            query = (
                "SELECT id, uri, clientId, requestTimeStamp FROM EA_Discovery.uri WHERE uri = %s AND clientId = %s "
                "AND requestTimeStamp = %s")
            # request_datetime = obj.get_request_timestamp()
            val = (obj.get_uri(), obj.get_client_id(), obj.get_request_timestamp())
            cursor.execute(query, val)
            record = cursor.fetchone()

            if record is not None:
                ret = domain.Uri.Uri(record[0], record[1], record[2], record[3])
                return ret
            else:
                return None

        except mysql.connector.errors.InterfaceError as ie:
            if ie.msg == 'No result set to fetch from.':
                # no problem, we were just at the end of the result set
                pass
            else:
                raise
        except mydb.connector.Error as e:
            print("Error reading data from MySQL table", e)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("in module", __name__)
        finally:
            if mydb.is_connected():
                mydb.close()
                cursor.close()

    @staticmethod
    def find_correlation(condition: domain.Uri.Uri, result: domain.Uri.Uri) -> domain.Correlation.Correlation:
        # busca uma correlação no banco de dados
        ret = None
        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor(buffered=True)
        try:

            query = (
                "SELECT id, fk_condition, fk_result, quantity FROM EA_Discovery.Correlation WHERE fk_condition = %s "
                "AND fk_result = %s")
            vals = (condition.get_id(), result.get_id())
            cursor.execute(query, vals)
            record = cursor.fetchone()

            if record is not None:
                ret = domain.Correlation.Correlation(record[0], record[1], record[2], record[3])

            return ret

        except mysql.connector.errors.InterfaceError as ie:
            if ie.msg == 'No result set to fetch from.':
                # no problem, we were just at the end of the result set
                pass
            else:
                raise
        except mydb.connector.Error as e:
            print("Error reading data from MySQL table", e)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()

    @staticmethod
    def find_correlation(condition: domain.Uri.Uri, result: domain.Uri.Uri) -> domain.Correlation.Correlation:
        # busca uma correlação no banco de dados
        ret = None

        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor(buffered=True)
        try:

            query = (
                "SELECT id, fk_condition, fk_result, quantity FROM EA_Discovery.Correlation WHERE fk_condition = %s "
                " AND fk_result = %s")
            vals = (condition.get_id(), result.get_id())
            cursor.execute(query, vals)
            record = cursor.fetchone()

            if record is not None:
                ret = domain.Correlation.Correlation(record[0], record[1], record[2], record[3])

            return ret

        except mysql.connector.errors.InterfaceError as ie:
            if ie.msg == 'No result set to fetch from.':
                # no problem, we were just at the end of the result set
                pass
            else:
                raise
        except mydb.connector.Error as e:
            print("Error reading data from MySQL table", e)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()

    @staticmethod
    def find_correlation_repeated_attributes(correlation_id, condition_attribute_name,
                                             result_attribute_name,
                                             attribute_value) -> domain.RepeatedAttributes.ReapeatedAttributes:

        ret: domain.RepeatedAttributes.ReapeatedAttributes = None  # guarda o retorno

        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor(buffered=True)

        try:
            query = (
                "SELECT correlation_id, condition_attribute_name, result_attribute_name, attribute_value, quantity, probability"
                " FROM EA_Discovery.ReapeatedAttributes WHERE correlation_id=%s "
                " AND condition_attribute_name=%s AND result_attribute_name=%s AND attribute_value=%s")
            val = (correlation_id, condition_attribute_name, result_attribute_name, attribute_value)
            cursor.execute(query, val)
            record = cursor.fetchone()

            if record is not None:
                ret = domain.RepeatedAttributes.ReapeatedAttributes(record[0], record[1], record[2], record[3])
                ret.set_quantity(record[4])
                # if record[5] is not None: #TODO tratar probability

            return ret

        except mysql.connector.errors.InterfaceError as ie:
            if ie.msg == 'No result set to fetch from.':
                # no problem, we were just at the end of the result set
                pass
            else:
                raise
        except mydb.connector.Error as e:
            print("Error reading data from MySQL table", str(e))
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("in module", __name__)
        finally:
            if mydb.is_connected():
                mydb.close()
                cursor.close()

    @staticmethod
    def save_correlation(uri1: domain.Uri.Uri, uri2: domain.Uri.Uri) -> domain.Correlation.Correlation:
        """Cria ou atualiza a correlação
            Se uri não existir cria a uri
            itera nos atributos e atualiza o mapa de atributos da uri e das correspondencias na correlacao"""

        ret: domain.Correlation.Correlation = None  # guarda o retorno

        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor(buffered=True)

        if uri1.__eq__(uri2) and not uri2.is_valid():
            return None
        elif MySqlRepository.check_uri_required(uri1) and MySqlRepository.check_uri_required(uri2):
            try:

                # verifica se as uris já existem e recupera os id
                if MySqlRepository.find_uri(uri1) is None:
                    MySqlRepository.create_uri(uri1)
                if MySqlRepository.find_uri(uri2) is None:
                    MySqlRepository.create_uri(uri2)

                obj1 = MySqlRepository.find_uri(uri1)
                obj2 = MySqlRepository.find_uri(uri2)

                # verifica qual é o maior para registrar na ordem. Se obj2 > obj1 inverte
                if obj1.get_request_timestamp() > obj2.get_request_timestamp():
                    aux = obj2
                    obj2 = obj1
                    obj1 = aux

                # não grava se as duas URIs forem iguais
                if obj1.id != obj2.id:
                    correlation = MySqlRepository.find_correlation(obj1, obj2)
                    if correlation is None:
                        dml = "INSERT INTO EA_Discovery.Correlation (fk_condition, fk_result) VALUES (%s, %s)"
                        vals = (obj1.id, obj2.id)
                        cursor.execute(dml, vals)
                        mydb.commit()
                        new_correlation = domain.Correlation.Correlation(cursor.lastrowid, obj1.id, obj2.id, 1)
                        ret = new_correlation
                        # batch_id = cursor.execute('select last_insert_id() from batch'
                    else:
                        # incrementa a quantidade de correlacoes encontrada
                        qtd = correlation.get_quantity() + 1
                        dml = "UPDATE EA_Discovery.Correlation SET quantity=%s WHERE id=%s "
                        val = (qtd, correlation.id)
                        cursor.execute(dml, val)
                        mydb.commit()
                        correlation.set_quantity(qtd)
                        ret = correlation

                return ret

            except mysql.connector.errors.InterfaceError as ie:
                if ie.msg == 'No result set to fetch from.':
                    # no problem, we were just at the end of the result set
                    pass
                else:
                    raise
            except mydb.connector.Error as e:
                print("Error reading data from MySQL table in ", sys.modules[__name__], str(e))
                raise
            except Exception as error:
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("in module", __name__)
                raise
            finally:
                if mydb.is_connected():
                    mydb.close()
                    cursor.close()

    @staticmethod
    def save_correlation_repeated_attributes(correlation_id, condition_attribute_name,
                                             result_attribute_name,
                                             attribute_value) -> domain.RepeatedAttributes.ReapeatedAttributes:

        ret: domain.RepeatedAttributes.ReapeatedAttributes = None  # guarda o retorno
        rp_att: domain.RepeatedAttributes.ReapeatedAttributes = None

        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )
        cursor = mydb.cursor(buffered=True)

        if correlation_id > 0 and condition_attribute_name is not None and result_attribute_name is not None and attribute_value is not None:
            try:

                # find atributos para verificar se já existe e incrementar de 1
                rp_att = MySqlRepository.find_correlation_repeated_attributes(correlation_id, condition_attribute_name,
                                                                              result_attribute_name,
                                                                              attribute_value)
                if rp_att is None:
                    dml = "INSERT INTO EA_Discovery.ReapeatedAttributes (correlation_id, condition_attribute_name, " \
                          " result_attribute_name, attribute_value) VALUES (%s, %s, %s, %s) "
                    vals = (correlation_id, condition_attribute_name, result_attribute_name, attribute_value)
                    cursor.execute(dml, vals)
                    mydb.commit()
                    new_rp_att = domain.RepeatedAttributes.ReapeatedAttributes(correlation_id, condition_attribute_name, result_attribute_name, attribute_value)
                    ret = new_rp_att
                else:
                    # incrementa a quantidade de correlacoes encontrada
                    qtd = rp_att.get_quantity() + 1
                    dml = " UPDATE EA_Discovery.ReapeatedAttributes SET quantity=%s WHERE correlation_id=%s " \
                          " AND condition_attribute_name=%s AND result_attribute_name=%s AND attribute_value=%s "
                    val = (qtd, rp_att.get_correlation_id(), rp_att.get_condition_attribute_name(),
                           rp_att.get_result_attribute_name(), rp_att.get_attribute_value())
                    cursor.execute(dml, val)
                    mydb.commit()
                    rp_att.set_quantity(qtd)
                    ret = rp_att
                return ret
            except mysql.connector.errors.InterfaceError as ie:
                if ie.msg == 'No result set to fetch from.':
                    # no problem, we were just at the end of the result set
                    pass
                else:
                    raise
            except mydb.connector.Error as e:
                print("Error reading data from MySQL table", str(e))
                print("in module", __name__)
                raise
            except Exception as error:
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("in module", __name__)
                raise
            finally:
                if mydb.is_connected():
                    mydb.close()
                    cursor.close()
        return ret

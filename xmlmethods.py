import oracledb
import os
import xml.etree.cElementTree as ET

error_codes = {942:"Tabela o podanej nazwie nie istnieje!", 2291:"Podano błędny klucz obcy!", 
               1:"Podany klucz główny już istnieje lub klucz obcy jest już wykorzystywany w innym rekordzie dla połączenia 1:1!",
               12899:"Podany za dużą wartość dla kolumny!", 947:"Nie podano wszystkich wymaganych wartości!"}

# write to xml from database

def export_xml(table_name, USER, PASSWORD, DSN, path = os.path.realpath(os.path.dirname(__file__))+"/tables"):
    connection = oracledb.connect(
        user=USER,
        password=PASSWORD,
        dsn=DSN
    ) 

    data = ET.Element(table_name)

    cursor = connection.cursor()

    cursor.execute(f"select * from {table_name}")
    rows = cursor.fetchall()
    rows.sort(key=lambda x: x[0])
    #print(rows)
    #for col in cursor.description: print(col)

    for row in rows:
        element = ET.SubElement(data,f"{table_name}-element")
        for id,col in enumerate(cursor.description):
            col_name = col[0]
            data_type = str(col[1])

            #element.set(col_name,str(row[id]))
            sub_ele = ET.SubElement(element,col_name)
            if data_type.find("NUMBER") > 0: sub_ele.set('type','int')
            sub_ele.text = str(row[id]).replace(' 00:00:00','')

    cursor.close()

    xml = ET.tostring(data,"UTF-8")
    with open(path+f"/{table_name}.xml","wb") as f:
        f.write(xml)
    
    connection.close()


def xml_data_to_list(root):
    res = []
    for child in root:
        ele = []
        for element in child:
            if ("type","int") in element.attrib.items():
                ele.append(int(element.text))
            else: 
                ele.append(element.text)
        res.append(tuple(ele))
    return res

def insert_to_database(root, USER, PASSWORD, DSN):
    connection = oracledb.connect(
        user=USER,
        password=PASSWORD,
        dsn=DSN
    ) 

    cursor = connection.cursor()

    values = xml_data_to_list(root)

    row_size = len(values[0])

    value_placeholder = "values("+ ", ".join([':'+str(i+1) for i in range(row_size)]) +")"

    cursor.executemany(f"insert into {root.tag} {value_placeholder}",values)
    connection.commit()
    export_xml(root.tag, USER, PASSWORD, DSN)
    cursor.close()
    connection.close()


if __name__ == "__main__":
    #export_xml("hotel")

    path = os.path.realpath(os.path.dirname(__file__))+"/tables"

    # tree = ET.parse(path+"/test2.xml")
    # root = tree.getroot()

    # insert_to_database(root)

    # print(root.tag)
    # print(len(root))

    # print(("type","int") in root.attrib.items())

    # print(xml_data_to_list(root))

    # row_size = 4
    # value_placeholder = "values("+ ", ".join([':'+str(i+1) for i in range(row_size)]) +")"

    # print(value_placeholder)

    # for child in root:
    #     for element in child:
    #         print(element.tag,element.text)
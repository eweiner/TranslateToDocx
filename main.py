import sqlite3
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor

def write_table_to_document(content, document, table, tableName):
    schema = table[tableName]
    document.add_paragraph(tableName, style = "Heading 1")
    for i in range(0, len(content)):
        document.add_paragraph(tableName + " " + str(i + 1) + "\n", style = "Heading 2")
        for j in range(0, len(content[i])):
            document.add_paragraph(schema[j] + ": " + str(content[i][j]), style = "ListBullet")
            document.add_paragraph("\n")


def get_resources(conn):
    sql = 'SELECT * FROM Resources'
    c = conn.cursor()
    c.execute(sql)
    all_rows = c.fetchall()
    return all_rows


def get_path_settings(conn):
    sql = 'select PathSettingsId,PathSettingsName,LastChange from PathSettings;'
    c = conn.cursor()
    c.execute(sql)
    all_rows = c.fetchall()
    return all_rows


def get_security_envs(conn):
    sql = 'select SecurityEnvironmentId,SecurityEnvironmentName,LastChange from SecurityEnvironments;'
    c = conn.cursor()
    c.execute(sql)
    all_rows = c.fetchall()
    return all_rows

def initializeDoc(path):
    document = Document()
    styles = document.styles()

    return styles, document

def createStyle(style, wd_style, fontName, size, name = 'Times New Roman', color=[0, 0, 0], biu = [False, False, False]):
    charstyle = style.add_style(fontName, wd_style)
    font = charstyle.font
    font.name = name
    font.size = Pt(size)
    font.bold = biu[0]
    font.italic = biu[1]
    font.underline = biu[2]
    font.color.rgb = RGBColor(color[0], color[1], color[2])

#Iterate through sqlite_master which has a lot of extraneous data in order to find the schema of a table
#Returns a dictionary with a key as the name of the category and the contents the variable names
def get_schema(conn):
    sql = 'SELECT * FROM sqlite_master'
    c = conn.cursor()
    c.execute(sql)
    sqlite_master = c.fetchall()
    table = {}

    for element in sqlite_master:
        tableElement = []
        if (element[4] != None):
            if (element[4].find("(") != -1):
                tableName = element[1]
                rawElement = element[4][element[4].index("(") + 1:].split(",")
                for element in rawElement:
                    temp = element.strip()
                    #Remove mentions of dependencies, may remove
                    if (temp.find("FOREIGN") == -1):
                        if(temp.find(" ") != -1):
                            temp = temp[:temp.find(" ")]
                        tableElement.append(temp)

                table[tableName] = tableElement
    return table

def open_db(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def main():
    db_file = "/Users/ericweiner/Downloads/TestSDB.sdb"
    conn = open_db(db_file)
    table = get_schema(conn)
    resources = get_resources(conn)
    path_settings = get_path_settings(conn)
    security_environments = get_security_envs(conn)
    document = Document()
    write_table_to_document(resources, document, table, "Resources")
    write_table_to_document(path_settings, document, table, "PathSettings")
    write_table_to_document(security_environments, document, table, "SecurityEnvironments")
    document.save("/Users/ericweiner/Documents/test.docx")


main()

#start with resources


__author__ = 'ericweiner'
import sqlite3

class DBSScraper():

    def get_resources_table(self, conn):
        ressql = 'SELECT * FROM Resources'
        c = conn.cursor()
        c.execute(ressql)
        resources = []
        raw_resources = c.fetchall()
        for i in range(0, len(raw_resources)):
            pathsql = 'SELECT PathSettingsName FROM PathSettings WHERE PathSettingsId = ' + str(raw_resources[i][2])
            c.execute(pathsql)
            path_settings_name = c.fetchone()
            secsql = 'SELECT SecurityEnvironmentName FROM SecurityEnvironments WHERE SecurityEnvironmentId = ' + str(raw_resources[i][3])
            c.execute(secsql)
            sec_env_name = c.fetchone()
            resources.append((raw_resources[i][0], raw_resources[i][1], path_settings_name[0], sec_env_name[0], raw_resources[i][4]))
        return resources

    def get_path_settings_table(self, conn):
        sql = 'select PathSettingsId,PathSettingsName,LastChange from PathSettings;'
        c = conn.cursor()
        c.execute(sql)
        all_rows = c.fetchall()
        return all_rows

    def get_security_envs_table(self, conn):
        sql = 'select SecurityEnvironmentId,SecurityEnvironmentName,LastChange from SecurityEnvironments;'
        c = conn.cursor()
        c.execute(sql)
        all_rows = c.fetchall()
        return all_rows

    def __init__(self, fileName):
        self.fileName = fileName
        self.conn = sqlite3.connect(fileName)
        sql = 'SELECT * FROM sqlite_master'
        c = self.conn.cursor()
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
        self.table = table
        self.resources = self.get_resources_table(self.conn)
        self.path_settings = self.get_path_settings_table(self.conn)
        self.security_envs = self.get_security_envs_table(self.conn)

    def get_resources(self):
        return self.resources

    def get_path_settings(self):
        return self.path_settings

    def get_security_envs(self):
        return self.security_envs

    def get_table(self):
        return self.table

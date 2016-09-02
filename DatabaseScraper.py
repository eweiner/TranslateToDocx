__author__ = 'ericweiner'
import sqlite3
from bs4 import BeautifulSoup

class DBSScraper():

    #Not Yet Implemented
    def parse_Security_Envs(self, conn):
        finalDict = {}
        allDicts = {}
        allAlgs = []
        sql2 = 'select SecurityEnvironmentId from SecurityEnvironments;'
        c = conn.cursor()
        c.execute(sql2)
        all_ids = [item[0] for item in c.fetchall()]
        for se_id in all_ids:
            sql2 = 'select SecurityEnvironment from SecurityEnvironments where SecurityEnvironmentId = ?;'
            c = conn.cursor()
            c.execute(sql2, [se_id])
            all_rows = [item[0] for item in c.fetchall()]
            for row in all_rows:
                soup = BeautifulSoup(row, "lxml")
                se = soup.findAll("se")
                if se and 1 == len(se):
                    for c in se[0].contents:
 #                       if Tag is type(c) and "px" == c.name:
                        if "px" == c.name:
                            for ic in c.contents:
#                                if Tag is type(ic):
                                    name = ic.name
                                    if name == "m_prohibitedalgs":
                                        s = ic.encode()
                                        soup2 = BeautifulSoup(s, "lxml")
                                        oids = soup2.find_all("oid", text=True)
                                        for oid in oids:
                                            allAlgs.append(oid.text)
                                    elif name == "m_minkeysizes":
                                        s = ic.encode()
                                        soup2 = BeautifulSoup(s, "lxml")
                                        items = soup2.findAll("item")
                                        for item in items:
                                            first = item.findAll("first")
                                            second = item.findAll("second")
                                            first = first[0].text
                                            second = second[0].text
                                            allDicts[first] = second
        finalDict['algs'] = allAlgs
        finalDict['keys'] = allDicts

        return finalDict

    def parse_path_settings(self, conn):
        count = 1
        allDicts = {}
        sql2 = 'select PathSettingsId from PathSettings;'
        c = conn.cursor()
        c.execute(sql2)
        all_ids = [item[0] for item in c.fetchall()]
        while count < len(all_ids)+1:
            sql2 = 'select PathSettings from PathSettings where PathSettingsId = ?;'
            c = conn.cursor()
            c.execute(sql2, [count])
            all_rows = [item[0] for item in c.fetchall()]
            for row in all_rows:
                soup = BeautifulSoup(row, "lxml")
                items = soup.findAll("item")
                first = ""
                value = ""
                PSdict = {}

                #make value2 a list and add the values to the list that apply to each key
                for item in items:
                    seconds = item.findAll("second")
                    firsts = item.findAll("first")
                    if len(firsts) == 0:
                        first = None
                    else:
                        first = firsts[0].text
                    for second in seconds:
                        which = second.findAll("which")
                        value = second.findAll("value")
                        which = which[0].text
                        value = value[0].text
                        if which == '0' and value == '0':
                            value3 = False
                            PSdict[first] = value3
                        if which == '0' and value == '1':
                            value3 = False
                            PSdict[first] = value3
                        else:
                            PSdict[first] = value.replace("\n", " ")
                allDicts[count] = PSdict
                count += 1
        return allDicts

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


    def tupleToList(self, listOfTuples):
        for i in range(0, len(listOfTuples)):
            listOfTuples[i] = list(listOfTuples[i])
        return listOfTuples

    def listToTuple(self, listOfLists):
        for i in range(0, len(listOfLists)):
            listOfLists[i] = tuple(listOfLists[i])
        return listOfLists

    def get_path_settings_table(self, conn):
        sql = 'select PathSettingsId,PathSettingsName,LastChange from PathSettings;'
        c = conn.cursor()
        c.execute(sql)
        all_rows = c.fetchall()
        dict = self.parse_path_settings(conn)
        temp = self.tupleToList(all_rows)
        for i in range(0, len(temp)):
            temp[i].insert(2, self.path_setting_blob)
        all_rows = self.listToTuple(temp)
        return all_rows



    def get_security_envs_table(self, conn):
        sql = 'select SecurityEnvironmentId,SecurityEnvironmentName,LastChange from SecurityEnvironments;'
        c = conn.cursor()
        c.execute(sql)
        all_rows = c.fetchall()
        dict = self.parse_Security_Envs(conn)
        temp = self.tupleToList(all_rows)
        for i in range(0, len(temp)):
            temp[i].insert(2, self.security_envs_blob)
        all_rows = self.listToTuple(temp)
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
        self.path_setting_blob = self.parse_path_settings(self.conn)
        self.path_settings = self.get_path_settings_table(self.conn)
        self.security_envs_blob = self.parse_Security_Envs(self.conn)
        self.security_envs = self.get_security_envs_table(self.conn)


    def get_resources(self):
        return self.resources

    def get_path_settings(self):
        return self.path_settings

    def get_security_envs(self):
        return self.security_envs

    def get_table(self):
        return self.table

    def get_conn(self):
        return self.conn

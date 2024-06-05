#!/usr/bin/env python3

import argparse
from rich.table import Table
from rich.console import Console
import json
from getpass import getpass
import os
import os.path

from cryptography.fernet import Fernet
import pyAesCrypt as aes
import tempfile 


class CPM():
    def __init__(self, bufferSize:int=64*1024) -> None:
        self.bufferSize = bufferSize    

    def saveDB(self, data: dict, file:str, passwd:str) -> None:
        tmpFile = tempfile.NamedTemporaryFile(delete=False)
        with open(tmpFile.name, 'w') as tmp:
            json.dump(data, tmp, indent=2)
        aes.encryptFile(tmpFile.name, file, passwd)
        os.unlink(tmpFile.name)
    
    def openDB(self, inFile:str, passwd:str) -> dict:
        with open(inFile,'rb') as inFile:
            try:
                tmpFile = tempfile.NamedTemporaryFile(delete=False)
                with open(tmpFile.name, "wb") as outFile:
                    aes.decryptStream(inFile,outFile,passwd,self.bufferSize)
            except ValueError:
                print("Wrong password ! Access denied !")
                os.remove(tmpFile.name)
                quit()

            with open(tmpFile.name, "r") as outFile:
                data = json.load(outFile)
                os.remove(tmpFile.name)
            return data

    def createDB(self, fileName:str,passwd:str) -> None:
        key = Fernet.generate_key().decode()
        initDB = {
            "key":key,
            "intents":[{
                    "title":"TITLE",
                    "username":"USERNAME",
                    "password":self.encrypt_passwd("PASSWORD",key),
                    "description":"DESCRIPTION"
                }]}
        
        tmpFile = tempfile.NamedTemporaryFile(delete=False)
        with open(tmpFile.name,"w") as file:
            json.dump(initDB, file, indent=2)
        self.saveDB(tmpFile.name,fileName,passwd)
        os.unlink(tmpFile.name)

    def encrypt_passwd(self, passwd:str, key:str) -> str:
        fernet = Fernet(key.encode())
        return fernet.encrypt(passwd.encode()).decode()

    def decrypt_passwd(self, encryptPasswd:str, key:str) -> str:
        fernet = Fernet(key.encode())
        return fernet.decrypt(encryptPasswd.encode()).decode()

    def find_by_title(self, title:str, intents:list[dict]) -> list:
        return [entry for entry in intents if entry["title"] == title]  

    def find_by_username(self, username:str, intents:list[dict]) -> list:
        return [entry for entry in intents if entry["username"] == username]  

    def add(self, title:str, username:str, passwd:str, description:str, data:dict, key:str) -> dict:
        entry = {'title':title,'username':username,'password':self.encrypt_passwd(passwd, key), "description":description}
        data["intents"].append(entry)
        return data
        
    def delete(self, entry:dict, data:dict) -> dict:
        for idx,_entry in enumerate( data["intents"]):
            if _entry == entry:
                data["intents"].pop(idx)
        return data
        

class Parser(argparse.ArgumentParser):
    def __init__(self):
        argparse.ArgumentParser.__init__(self,prog="cpm",description="CLI Password Manager")
        self.add_argument("--file","-f",metavar="FILE",type=str,help="JSON database file")
        self.add_argument("--login","-l",metavar="LOGIN",type=str,help="Specify login",)
        self.add_argument("--password","-p",metavar="PASSWORD",type=str,help="Specify password")
        self.add_argument("--title","-t",metavar="TITLE",type=str,help="Specify title")
        self.add_argument("--description","-d",metavar="DESCRIPTION",type=str,help="Add a description")
        self.add_argument("--all","-a",action='store_true',help="Delete/Show all entries")
        self.add_argument("function",choices=["add","delete","show"])
        self.args = self.parse_args()

class CPM_Table(Table):
    def __init__(self) -> None:
        Table.__init__(self,title="\nCLI Password Manager\n", title_justify="center")
        self.add_column("Title", justify="center",style="bold blue")
        self.add_column("Username", justify="center",style="blue")
        self.add_column("Password",justify="center",style="red")
        self.add_column("Description",justify="center",style="white")

    def show(self) -> None:
        Console().print(self)


if __name__ == '__main__':

    parser = Parser()
    args = parser.parse_args()
    table = CPM_Table()
    cpm = CPM()

    if not args.file:
        response = input("Do you want to create a new database file ? (yes/no) : ")
        while response.lower() != "yes" and response.lower() != "no":
            response = input("Do you want to create a new database file ? (yes/no) : ")

        if response.lower() == "yes":
            file_path = input("Give a path for your new file : ")
            if os.path.exists(file_path):
                print("This file path already exists !")
                quit()
            else:
                try:
                    master_passwd = getpass("Enter a master password : ") 
                    confirm = getpass("Confirm : ")
                    assert master_passwd == confirm
                    cpm.createDB(file_path, master_passwd)
                except AssertionError:
                    print("Error : not same password !")
                    quit()

                
        elif response.lower() == "no":
            file_path = input("Which file do you want to use ? : ")
            if not os.path.isfile(file_path):
                print("This is not a file path !")
                quit()
            elif not os.path.exists(file_path):
                print("This file path does not exist !")
                quit()
            else :
                master_passwd = getpass("Master password : ")
    else:
        file_path = args.file
        master_passwd = getpass("Master password : ")
                
    file_content = cpm.openDB(file_path, master_passwd)
    key = file_content["key"]

    if args.function == "show":

        if args.all:
            for data in file_content["intents"]:
                table.add_row(data["title"],data["username"],cpm.decrypt_passwd(data["password"],file_content["key"]),data["description"])
            table.show()
        elif args.login:
            for data in cpm.find_by_username(args.login, file_content["intents"]) :
                table.add_row(data["title"],data["username"],cpm.decrypt_passwd(data["password"],file_content["key"]),data["description"]) 
            table.show()
        elif args.title:
            for data in cpm.find_by_title(args.title, file_content["intents"]) :
                table.add_row(data["title"],data["username"],cpm.decrypt_passwd(data["password"],file_content["key"]),data["description"]) 
            table.show()
        else:
            print("You must specify a login or a title")
        quit()
    
    elif args.function == "add":
        
        title = input("Enter a title : ") if not args.title else args.title
        login = input("Enter a username : ") if not args.login else args.login
        password = getpass("Enter a password : ") if not args.password else args.password
        description = input("Enter a description : ") if not args.description else args.description

        new_data = cpm.add(title,login,password,description,file_content,key)
        table.add_row(title,login,password,description)  
        table.show()
    
    elif args.function == "delete":

        if args.all:
            
            confirm = input("Are you sure to delete all entries ? ")
            double_check = input("Are you very sure to delete all entries ? ")
            if confirm.lower() == double_check.lower() == "yes":
                file_content["intents"] = []
                print("All entries were removed.")

        else:
            title = input("Enter a title : ") if not args.title else args.title
            data = cpm.find_by_title(title, file_content["intents"])
            for entry in data:
                confirm = input("Are you sure to delete this entry ? ")
                if not confirm.lower() == "yes":
                    quit()
                new_data = cpm.delete(entry,file_content)
                print(f"{title} was remove.")

    cpm.saveDB(new_data,file_path, master_passwd)

            

        
                    

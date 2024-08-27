"""
    'FTPro', um programa que facilita upload de vários
    arquivos para um determinado servidor via FTP.
    ------------------------------------------------------

    Programa criado por: Luiz Gabriel Magalhães Trindade.
    ------------------------------------------------------

    Programa Licenciado sob a Licença MIT.
    https://mit-license.org/

    Copyright © 2024 <Luiz Gabriel Magalhães Trindade>

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the “Software”), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or 
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
    BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#Importação de bibliotecas
from customtkinter import *
import ftputil
import socket
from tkinter import filedialog, PhotoImage
from sqlite3 import *
from os import *

#Instância do sqlite3
initialSQL = """
    CREATE TABLE IF NOT EXISTS servers(
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        host        TEXT UNIQUE NOT NULL
    );
"""
conn = connect("_internal/FTProDatabase.db")
cursor = conn.execute(initialSQL)
conn.commit()

#Variáveis
timeout = 10
filesToUpload = []
serversList = []
checkboxes = {}  # Dicionário para armazenar os checkboxes

#Funções
#Luiz Trindade - Função de alerta para mensagens de erro ou sucesso
def alert(message):
    toplevel = CTkToplevel()
    toplevel.attributes("-topmost", True)
    toplevel.title(message)
    #toplevel.geometry(f"{int((len(message) * 100) / 8)}x100")
    toplevel.geometry("450x150")
    toplevelMessage = CTkLabel(
        master=toplevel, 
        text=message,
        font=("Arial", 12, "bold"),
        wraplength=300
    )
    #toplevelMessage.pack(padx=10, pady=10)
    toplevelMessage.pack(padx=10, pady=10, expand=True, fill='both')

    closeButton = CTkButton(
        master=toplevel,
        text="OK",
        command=toplevel.destroy
    )
    closeButton.pack(pady=10)

    toplevel.mainloop()
    # print(message)

#Luiz Trindade - Função para executar consultas SQL
def executeSQL(query):
    try:
        if "SELECT" in query:
            return cursor.execute(query).fetchall()
        
        else:
            cursor.execute(query)
            conn.commit()

    except Exception as error:
        alert(error)

def setFilesToUpload():
    global filesToUpload
    filesToUpload = []
    try:
        filesToUpload = filedialog.askopenfilenames()
        print("Files selected successfully!")
    except Exception as e:
        alert(e)

def uploadFilesFtputil(host, user, password, files_to_upload, remote_path):
    global timeout
    try:
        print(f"Connecting to {host}")

        with ftputil.FTPHost(host, user, password, timeout=timeout) as host:
            print("Success!")

            for file in files_to_upload:
                remote_file_path = f"{remote_path}/{path.basename(file)}"
                host.upload_if_newer(file, remote_file_path)

        alert("FILES UPLOADED SUCCESSFULLY!")
    except (socket.timeout) as e:
        alert(f"Connection error: {e}")

    except Exception as e:
        alert(f"Error: {e}")

def uploadFilesForAllServers():
    global filesToUpload, directory
    user        = str(userEntry.get())
    password    = str(passwordEntry.get())
    path        = str(pathEntry.get())

    servers = executeSQL("SELECT * FROM servers")

    #Itera sobre os checkboxes e imprime os nomes dos servidores selecionados
    selecionados = []
    for index, var in checkboxes.items():
        if var.get() == 1:
            servidor = servers[index][1] 
            selecionados.append(servidor)
    print("Servidores Selecionados:", selecionados)

    for servidor in selecionados:
        uploadFilesFtputil(servidor, user, password, filesToUpload, path)

#Luiz Trindade - Função para confirmar os arquivos selecionados
def confirmSelectedFiles():
    #Se confirmado, faz upload e fecha a janela de confirmação
    def uploadAndCloseTopLevel():
        uploadFilesForAllServers()
        toplevel.destroy()

    toplevel = CTkToplevel(master=app)
    toplevel.title("Confirm files before upload")
    toplevel.geometry("600x300")
    toplevel.attributes("-topmost", True)

    # Configurar o grid para expandir o frame scrollable e os botões
    toplevel.grid_rowconfigure(0, weight=1)  # Linha do frame scrollable
    toplevel.grid_rowconfigure(1, weight=0)  # Linha dos botões
    toplevel.grid_columnconfigure(0, weight=1)  # Coluna do frame scrollable
    toplevel.grid_columnconfigure(1, weight=1)  # Coluna dos botões

    filesScroll = CTkScrollableFrame(master=toplevel, width=500, height=200)
    filesScroll.grid(row=0, column=0, columnspan=2,padx=10, pady=10, sticky="nsew")

    for file in filesToUpload:
        labelFile = CTkLabel(
            master=filesScroll,
            text=f"{file}",
            font=("Arial", 10, "bold")
        )
        labelFile.pack(padx=10, pady=1, anchor="w")

    confirmButton = CTkButton(
        master=toplevel,
        text="CONFIRM",
        font=("Arial", 15, "bold"),
        fg_color="green",
        command=uploadAndCloseTopLevel
    ).grid(row=1, column=0, columnspan=1, padx=5, pady=20)

    cancelButton = CTkButton(
        master=toplevel,
        text="CANCEL",
        font=("Arial", 15, "bold"),
        fg_color="red",
        command=toplevel.destroy
    ).grid(row=1, column=1, columnspan=1, padx=5, pady=20)


    toplevel.mainloop()

#Luiz Trindade - Função para adicionar um host
def addHost():
    dialog = CTkInputDialog(text="HOST ADRESS:", title="ADD HOST")
    dialog.attributes("-topmost", True)
    host = dialog.get_input()

    if len(host) > 0:
        executeSQL(f"""
            INSERT INTO servers(host)
            VALUES(
                '{host}'
            );
        """)
        loadAndShowServers()

#Luiz Trindade - Função para deletar um host
def removeHost():
    dialog = CTkInputDialog(text="HOST ADRESS:", title="REMOVE HOST")
    dialog.attributes("-topmost", True)
    host = dialog.get_input()

    if len(host) > 0:
        executeSQL(f"""
            DELETE FROM servers WHERE host = '{host}'
        """)
        loadAndShowServers()

#Interface
app = CTk()
app.title("FTPro")
app.geometry("850x600")
#Descomente se estiver no Windows
#app.iconbitmap("_internal/icons/icon.ico") 

app_icon = PhotoImage(file="_internal/icons/icon.png")
app.iconphoto(True, app_icon)

app.grid_columnconfigure(0, weight=1)  # Configura a coluna 0
app.grid_columnconfigure(1, weight=1)  # Configura a coluna 1

set_appearance_mode("dark")
set_widget_scaling(1.4)

tabview = CTkTabview(master=app)
tabview.pack(padx=10, pady=0)

serversTab  = tabview.add("SERVERS")
aboutTab    = tabview.add("ABOUT")

#ServersTab
serversTabFrameShow = CTkFrame(master=serversTab, width=200, height=100)
serversTabFrameShow.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

serversTabFrame = CTkScrollableFrame(master=serversTabFrameShow, width=300, height=100, fg_color="gray28")
serversTabFrame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

#Luiz Trindade - Função de renderização de servidores
def loadAndShowServers():
    # Limpa as checkboxes existentes
    for widget in serversTabFrame.winfo_children():
        widget.destroy()

    # Limpa o dicionário de checkboxes
    checkboxes.clear()

    serversList = executeSQL("SELECT * FROM servers")
    if len(serversList) > 0:
        for index, item in enumerate(serversList):
            var = IntVar()
            checkbox = CTkCheckBox(
                master=serversTabFrame, 
                text=f"{item[1]}", 
                variable=var,
                font=("Arial", 15, "bold"),
                text_color="white",
                fg_color="green"
            )
            checkbox.pack(padx=10, pady=5, anchor="w")
            checkboxes[index] = var
loadAndShowServers()

addServerButton = CTkButton(
    master=serversTabFrameShow,
    text="ADD HOST +",
    fg_color="green",
    font=("Arial", 15, "bold"),
    command=addHost
).grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

removeServerButton = CTkButton(
    master=serversTabFrameShow,
    text="REMOVE HOST -",
    fg_color="red",
    font=("Arial", 15, "bold"),
    command=removeHost
).grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

#--------------------------------------------------------------------

controlsFrame = CTkFrame(master=serversTab, width=300, height=200, fg_color="gray28")
controlsFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

userEntry = CTkEntry(
    master=controlsFrame,
    placeholder_text="User Name 👤",
    justify="center"
)
userEntry.pack(padx=10, pady=5)

passwordEntry = CTkEntry(
    master=controlsFrame,
    placeholder_text="Password 🔑",
    justify="center",
    show="*"
)
passwordEntry.pack(padx=10, pady=5)

pathEntry = CTkEntry(
    master=controlsFrame,
    placeholder_text="Path 📁",
    justify="center"
)
pathEntry.pack(padx=10, pady=5)

selectFilesToUpload = CTkButton(
    master=controlsFrame,
    text="SELECT FILES 📁",
    command=setFilesToUpload,
    font=("Arial", 15, "bold")
).pack(padx=10, pady=10)

uploadForAllButton = CTkButton(
    master=controlsFrame,
    text="UPLOAD \u2b06",
    command=confirmSelectedFiles,
    fg_color="green",
    font=("Arial", 15, "bold")
).pack(padx=10, pady=10)

#-------------------------------------------------------------

aboutScroll = CTkScrollableFrame(master=aboutTab, width=600, height=600)
aboutScroll.pack(padx=10, pady=10, expand=True, fill='both')

icon = CTkLabel(master=aboutScroll, image=app_icon, text=None)
icon.pack()


aboutText = """
A small and simple program called 'FTPro' 
that helps in sending multiple files to 
multiple servers at once. 

The program is written entirely in Python. 

Created by: Luiz Gabriel Magalhães Trindade. 
Licensed under the MIT License.
https://mit-license.org/
"""

aboutTextLabel = CTkLabel(
    master=aboutScroll,
    text=aboutText,
    justify="left",
    font=("Arial", 15, "bold")
)
aboutTextLabel.pack(padx=10, pady=10)

githubImage = PhotoImage(file="_internal/image/github.png")
image = CTkLabel(master=aboutScroll, image=githubImage, text=None)
image.pack(padx=10, pady=5)


app.mainloop()

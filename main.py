import mysql.connector as sql
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from functools import partial
from prettytable import PrettyTable
import re
import hashlib
import getpass
import datetime

global conn_obj
global cursr







class VotingSystemGUI:
    def __init__(self, root):
        self.user_data = None
        self.root = root
        self.root.title("Voting System")
        self.create_login_screen()
    

    # def validate_input(self,string, regex_pattern):
        
    #     user_input = input(string)
    #     if re.match(regex_pattern, user_input):
    #         return True
    #     else:
    #         return False


    def create_login_screen(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=20, pady=20)

        tk.Label(self.login_frame, text="Welcome to Voting System!", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.login_frame, text="Login as:").grid(row=1, column=0, sticky="e", pady=5)
        self.login_type_var = tk.StringVar()
        self.login_type_var.set("ADMIN")
        tk.OptionMenu(self.login_frame, self.login_type_var, "ADMIN", "VOTER").grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(self.login_frame, text="ID:").grid(row=2, column=0, sticky="e", pady=5)
        self.id_entry = tk.Entry(self.login_frame)
        self.id_entry.grid(row=2, column=1, pady=5)

        tk.Label(self.login_frame, text="Password:").grid(row=3, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)

        login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        login_button.grid(row=4, column=1, pady=10)

    def login(self):
        login_type = self.login_type_var.get().upper()
        user_id = self.id_entry.get()
        password = self.password_entry.get()

        if login_type == "ADMIN":
            if not validate_input(user_id,r'^\d+$'):
                messagebox.showerror("Please enter a valid User ID.")
                return

            name, self.user_data = login_admin(user_id, password)
            # Call your login_admin function with user_id and password
            # If login is successful, show admin dashboard
            # else show an error message
            if self.user_data:
                messagebox.showinfo("Login Successful", f"Welcome {name}!")
                self.id_entry.delete(0,tk.END)
                self.password_entry.delete(0,tk.END)
                self.show_admin_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")
        
        elif login_type == "VOTER":
            if not validate_input(user_id,r'^[A-Za-z0-9]{10}$'):
                messagebox.showerror("Please enter a valid User ID.")
                return
            name, self.user_data = login_voter(user_id, password)
            # Call your login_voter function with user_id and password
            # If login is successful, show voter dashboard
            # else show an error message
            if self.user_data:
                messagebox.showinfo("Login Successful", f"Welcome {name}!")
                self.id_entry.delete(0,tk.END)
                self.password_entry.delete(0,tk.END)
                self.show_voter_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")
        else:
            messagebox.showerror("Invalid Login Type", "Please select a valid login type.")

    def show_admin_dashboard(self):
        admin_dashboard_window = tk.Toplevel(self.root)
        admin_dashboard_window.title("Admin Dashboard")

        create_election_button = tk.Button(admin_dashboard_window, text="Create Election", command=self.create_election)
        create_election_button.pack(pady=10)

        # view_elections_button = tk.Button(admin_dashboard_window, text="View Elections", command=self.view_elections)
        # view_elections_button.pack(pady=10)

        view_candidates_button = tk.Button(admin_dashboard_window, text="View Candidates of an Election", command=self.view_candidates)
        view_candidates_button.pack(pady=10)

        view_details_button = tk.Button(admin_dashboard_window, text="View Election Details", command=self.view_details)
        view_details_button.pack(pady=10)

        make_changes_button = tk.Button(admin_dashboard_window, text="Make Changes in an Election", command=self.make_changes)
        make_changes_button.pack(pady=10)

        generate_results_button = tk.Button(admin_dashboard_window, text="Generate Election Results", command=self.generate_results)
        generate_results_button.pack(pady=10)

        logout_button = tk.Button(admin_dashboard_window, text="LOG OUT", command=admin_dashboard_window.destroy)
        logout_button.pack(pady=10)
    

    def show_voter_dashboard(self):
        voter_dashboard_window = tk.Toplevel(self.root)
        voter_dashboard_window.title("Voter Dashboard")

        welcome_label = tk.Label(voter_dashboard_window,text=f"Welcome {self.user_data[0]}", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        button_frame = tk.Frame(voter_dashboard_window)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        vote_button = tk.Button(button_frame, text="Vote in a Election", command=self.vote_in_election)
        vote_button.grid(row=0, column=0, padx=10, pady=5)

        logout_button = tk.Button(button_frame, text="Log Out", command=voter_dashboard_window.destroy)
        logout_button.grid(row=0, column=1, padx=10, pady=5)

        # vote_button = tk.Button(voter_dashboard_window, text="Vote in a Election", command=self.vote_in_election)
        # vote_button.pack(pady=10)

        # logout_button = tk.Button(voter_dashboard_window, text="Log Out", command=voter_dashboard_window.destroy)
        # logout_button.pack(pady=10)




    def vote(self, user_data, vote_in_election):
        cursr.execute(f"SELECT POST_ID, POSTNAME FROM POSTS WHERE ELECTIONID={vote_in_election}")
        posts = cursr.fetchall()
        
        def inner_vote(post_id, post_name, candidates):
            vote_window = tk.Tk()
            vote_window.geometry("500x500")
            vote_window.title("Vote for " + post_name)

            vote_label = tk.Label(vote_window, text="Select your candidate:")
            vote_label.pack()

            # for idx, candidate in enumerate(candidates):
            #     candidate_label = tk.Label(vote_window, text=str(idx+1) + ". " + candidate[1] + " (" + candidate[0] + ")")
            #     candidate_label.pack()

            vote_var = tk.IntVar()
            vote_var.set(1)

            def submit_vote():
                vote_choice = vote_var.get()
                if vote_choice <= len(candidates):
                    try:
                        sql = f"INSERT INTO VOTES VALUES ('{user_data[0]}', {vote_in_election}, {post_id}, '{candidates[vote_choice-1][0]}')"
                        cursr.execute(sql)
                        conn_obj.commit()
                        # frame.destroy()
                        messagebox.showinfo("Success", "Vote registered successfully!")
                        vote_window.quit()
                        # vote_window.destroy()
                        
                    except:
                        messagebox.showerror("Error", "Failed to register the vote.")
                else:
                    messagebox.showerror("Error", "Please enter a valid vote.")

            vote_radio = tk.Radiobutton(vote_window, variable=vote_var)
            vote_radio.pack_forget()  # Hide the first radio button

            for idx in range(len(candidates)):
                vote_radio = tk.Radiobutton(vote_window, variable=vote_var, value=idx+1, text=candidates[idx][1]+" ("+candidates[idx][0]+")")
                vote_radio.pack()

            submit_button = tk.Button(vote_window, text="Submit Vote", command=submit_vote)
            submit_button.pack()

            vote_window.mainloop()
            

        # Check if user already voted
        cursr.execute(f"SELECT VOTERID FROM VOTES WHERE ELECTIONID={vote_in_election} AND VOTERID=\'{user_data[0]}\'")
        temp = cursr.fetchall()
        if not temp:
            for post in posts:
                cursr.execute(f"SELECT USN, NAME FROM CANDIDATES WHERE ELECTIONID={vote_in_election} AND POSTID={post[0]}")
                candidates = cursr.fetchall()
                if candidates:
                    # frame = tk.Frame(vote_window)
                    inner_vote(post[0], post[1], candidates)
        else:
            messagebox.showinfo("Cannot Vote", "You have already voted for this election.")

        # Replace 'posts' with your actual list of posts
         # Example list of posts [(post_id, post_name)]

            
    
    
    def vote_in_election(self):
        def select_election(event):
            global election_id, elections
            selection = election_list.curselection()[0]  # Get selected index
            election_id = elections[selection][0]
            print("selected")
        
        def vote_candidates():
            if election_id:
                window.destroy()
                self.vote(self.user_data, election_id)

            else:
                print("No election selected")


        window = tk.Toplevel(self.root)
        window.title("VOTE")
        # text_label = tk.Label(window,text=f"Select the Election to Vote", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)


        cursr.execute(f"SELECT ELECTION_ID FROM ELECTION WHERE YEAR>={datetime.datetime.now().year} ") #AND \'{self.user_data[0]}\' NOT IN (SELECT DISTINCT VOTERID FROM VOTES)
        global elections
        elections = cursr.fetchall()

        # Check if there are any elections to display
        if not elections:
            messagebox.showerror("Error", "No elections found!")
            window.destroy()

        # Label for election selection
        election_label = tk.Label(window, text="Select the election:")
        election_label.pack()

        vote_button = tk.Button(window, text="Proceed to Vote", command=vote_candidates)
        vote_button.pack(pady=10)

        # Listbox to display elections
        election_list = tk.Listbox(window)
        for i, election in enumerate(elections):
            election_list.insert(tk.END, f"{i+1}. {election[0]}")
        election_list.bind("<<ListboxSelect>>", select_election)  # Bind select event
        election_list.pack()

    def create_election(self):
        def create_election_button_click():
            year = election_year_entry.get()
            if not validate_input(year,r'^\d{4}$'):
                messagebox.showerror("Please enter a valid Year.")
                return
            election_id = election_id_entry.get()
            if not validate_input(election_id,r'^\d+$'):
                messagebox.showerror("Please enter a valid Election Id.")
                return
            # Validate input and insert election values
            if year and election_id:
                try:
                    if int(year) <= datetime.date.today().year:
                        raise ValueError
                    insert_election_values(self.user_data[2], year, election_id)
                    messagebox.showinfo("Election Created", "Election has been created successfully!")
                    election_window.destroy()
                except:
                    messagebox.showwarning("Input Error", "Please fill proper values in all the fields.")

        election_window = tk.Toplevel(self.root)
        election_window.title("Create Election")

        # Create and place labels and entry widgets for admin ID, election year, and election ID

        tk.Label(election_window, text="Election Year:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        election_year_entry = tk.Entry(election_window)
        election_year_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(election_window, text="Election ID:").grid(row=2, column=0, pady=5, padx=5, sticky="e")
        election_id_entry = tk.Entry(election_window)
        election_id_entry.grid(row=2, column=1, pady=5, padx=5)

        create_button = tk.Button(election_window, text="Create Election", command=create_election_button_click)
        create_button.grid(row=3, column=1, pady=10)

        


    def view_elections(self):
        view_elections_window = tk.Toplevel(self.root)
        view_elections_window.title("View Elections Details")



    def view_candidates(self):
        def view_candidates_button_click():
            election_id = election_id_entry.get()
            if not validate_input(election_id,r'^\d+$'):
                messagebox.showerror("Please enter a valid Election Id.")
                return
            
            table = show_election_candidates(election_id)
            table_text = str(table)
            text_widget = tk.Text(view_candidates_window, wrap=tk.NONE, width=150)
            if table:
                text_widget.insert(tk.END, table_text)
            else:
                text_widget.insert(tk.END, "No Candidates found for the following election.")
            text_widget.grid(row=5,columnspan=4, pady=5, padx=5)


        view_candidates_window = tk.Toplevel(self.root)
        view_candidates_window.title("View Candidates.")

        tk.Label(view_candidates_window, text="Election ID:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        election_id_entry = tk.Entry(view_candidates_window)
        election_id_entry.grid(row=1, column=1, pady=5, padx=5)

        candidate_button = tk.Button(view_candidates_window, text="Fetch Details", command=view_candidates_button_click)
        candidate_button.grid(row=3, column=1, pady=10)



    def view_details(self):

        def election_details_button_click():
            election_id = election_id_entry.get()
            if not validate_input(election_id,r'^\d+$'):
                messagebox.showerror("Please enter a valid Election Id.")
                return
            table, year = show_election_details(self.user_data[2], election_id)
            table_text = table.get_string(title="Posts:")
            table_text = f"Election ID: {election_id} \n Year: {year} \n"+table_text
            text_widget = tk.Text(election_details_window, wrap=tk.NONE, width=150)
            if table and year:
                text_widget.insert(tk.END, table_text)
            else:
                text_widget.insert(tk.END, "No Candidates found for the following election.")
            text_widget.grid(row=5,columnspan=4, pady=5, padx=5)

        election_details_window = tk.Toplevel(self.root)
        election_details_window.title("View Election Details.")

        tk.Label(election_details_window, text="Election ID:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        election_id_entry = tk.Entry(election_details_window)
        election_id_entry.grid(row=1, column=1, pady=5, padx=5)

        candidate_button = tk.Button(election_details_window, text="Fetch Details", command=election_details_button_click)
        candidate_button.grid(row=3, column=1, pady=10)

    
    
    def make_changes(self):
        # Implement the functionality to make changes in an election
        # You may prompt the user for input, perform necessary operations, and display the results
        pass

    
    
    def generate_results(self):
        def select_election(event):
            global election_id, elections
            selection = election_list.curselection()[0]  # Get selected index
            election_id = elections[selection][0]

        # Function to handle plot choice
        def choose_plot(value):
            global plot_choice
            plot_choice.set(value)

        # Function to simulate generating results (replace with your logic)
        def generate():
            messagebox.showinfo("Result", f"Generating results for election ID: {election_id} (Plot: {plot_choice.get()})")
            if plot_choice.get() ==1:
                generate_result(election_id, 1)
            else:
                generate_result(election_id,2)
        # Initialize main window and election_id, plot_choice variables
        window = tk.Toplevel(self.root)
        window.title("Election Result Generator")
        cursr.execute(f"SELECT ELECTION_ID FROM ELECTION WHERE ADMINID={self.user_data[2]} AND ELECTION_ID IN (SELECT DISTINCT ELECTIONID FROM VOTE_COUNT)")
        global elections
        elections = cursr.fetchall()
        plot_choice = tk.IntVar()

        # Check if there are any elections to display
        if not elections:
            messagebox.showerror("Error", "No elections found!")
            window.destroy()

        # Label for election selection
        election_label = tk.Label(window, text="Select the election:")
        election_label.pack()

        # Listbox to display elections
        election_list = tk.Listbox(window)
        for i, election in enumerate(elections):
            election_list.insert(tk.END, f"{i+1}. {election[0]}")
        election_list.bind("<<ListboxSelect>>", select_election)  # Bind select event
        election_list.pack()

        # Radio buttons for plot type
        plot_frame = tk.Frame(window)
        plot_frame.pack()

        tk.Radiobutton(plot_frame, text="Bar Graph", variable=plot_choice, value=1).pack()
        tk.Radiobutton(plot_frame, text="Pie Chart", variable=plot_choice, value=2).pack()

        # Button to generate results
        generate_button = tk.Button(window, text="Generate Results", command=generate)
        generate_button.pack()







def dbms_connect(password):
    global conn_obj
    global cursr
    try:
        conn_obj = sql.connect(host='localhost', user='root',passwd=password)
        cursr = conn_obj.cursor()
    except:
        print("Connection failed.")


def close_connection():
    global conn_obj, cursr
    cursr.close()
    conn_obj.commit()
    conn_obj.close()


def create_database():
    try:
        try:
            cursr.execute("USE ELECTIONS")
        except:
            cursr.execute("CREATE DATABASE ELECTIONS")
        # cursr.execute("CREATE DATABASE IF NOT EXISTS ELECTIONS")
            cursr.execute("USE ELECTIONS")
            print("Database creation successful.")
            create_tables()
            
    except Exception:
        print("Database creation failed due to the following Exception: \n"+Exception.__name__)


def create_tables():
    table_creation_queries = ["CREATE TABLE ADMIN (DEPARTMENT VARCHAR(5), NAME VARCHAR(30), ADMIN_ID INT , PHONE VARCHAR(11) , PASSWD CHAR(64) NOT NULL, PRIMARY KEY(ADMIN_ID,PHONE))",
                            "CREATE TABLE ELECTION (YEAR INT(4),ELECTION_ID INT PRIMARY KEY,ADMINID INT,FOREIGN KEY (ADMINID) REFERENCES ADMIN(ADMIN_ID) ON DELETE CASCADE)",
                            "CREATE TABLE POSTS (NO_OF_CANDIDATES INT, POST_ID INT, ELECTIONID INT, POSTNAME VARCHAR(15), PRIMARY KEY(POST_ID, ELECTIONID), FOREIGN KEY (ELECTIONID) REFERENCES ELECTION(ELECTION_ID) ON DELETE CASCADE)",
                            "CREATE TABLE VOTERS (USN VARCHAR(10), DEPARTMENT VARCHAR(5), NAME VARCHAR(30), PHONE VARCHAR(11) , EMAIL VARCHAR(30), SEMESTER INT(1), PASSWD CHAR(64), PRIMARY KEY(USN,PHONE))",
                            "CREATE TABLE CANDIDATES (USN VARCHAR(10), SEMESTER INT(1), POSTID INT, DEPARTMENT VARCHAR(5), NAME VARCHAR(30), PHONE VARCHAR(11) , EMAIL VARCHAR(30), ELECTIONID INT, GENDER CHAR, PRIMARY KEY(USN,PHONE), FOREIGN KEY(ELECTIONID) REFERENCES ELECTION(ELECTION_ID) ON DELETE SET NULL, FOREIGN KEY (POSTID) REFERENCES POSTS(POST_ID) ON DELETE SET NULL)",
                            "CREATE TABLE VOTES (VOTERID VARCHAR(10), ELECTIONID INT, POSTID INT, CANDIDATEID VARCHAR(10), PRIMARY KEY(ELECTIONID, POSTID, VOTERID), FOREIGN KEY(VOTERID) REFERENCES VOTERS(USN) ON DELETE CASCADE, FOREIGN KEY(ELECTIONID) REFERENCES ELECTION(ELECTION_ID) ON DELETE CASCADE, FOREIGN KEY (POSTID) REFERENCES POSTS(POST_ID) ON DELETE CASCADE, FOREIGN KEY (CANDIDATEID) REFERENCES CANDIDATES(USN))",
                            "CREATE TABLE VOTE_COUNT (CANDIDATEID VARCHAR(10), ELECTIONID INT, POSTID INT, TOTAL_VOTES INT, PRIMARY KEY (CANDIDATEID, ELECTIONID, POSTID), FOREIGN KEY(CANDIDATEID) REFERENCES CANDIDATES(USN) ON DELETE CASCADE, FOREIGN KEY(ELECTIONID) REFERENCES ELECTION(ELECTION_ID) ON DELETE CASCADE, FOREIGN KEY(POSTID) REFERENCES POSTS(POST_ID) ON DELETE CASCADE)",
                            "CREATE TRIGGER UPDATE_NO_OF_CANDIDATES AFTER INSERT ON CANDIDATES FOR EACH ROW UPDATE POSTS SET NO_OF_CANDIDATES = NO_OF_CANDIDATES + 1 WHERE POST_ID = NEW.POSTID AND ELECTIONID = NEW.ELECTIONID",
                            "CREATE TRIGGER candidate_insert_trigger AFTER INSERT ON CANDIDATES FOR EACH ROW INSERT INTO VOTE_COUNT (CANDIDATEID, ELECTIONID, POSTID, TOTAL_VOTES) VALUES (NEW.USN, NEW.ELECTIONID, NEW.POSTID, 0)",
                            "CREATE TRIGGER update_vote_count AFTER INSERT ON VOTES FOR EACH ROW UPDATE VOTE_COUNT SET TOTAL_VOTES = TOTAL_VOTES + 1 WHERE CANDIDATEID= NEW.CANDIDATEID AND ELECTIONID = NEW.ELECTIONID AND POSTID = NEW.POSTID"]
    print("\nCreating all tables...")
    for i in table_creation_queries:
        try:
            cursr.execute(i)
        except:
            print("Error craeting table ",i[12:i.find('(')])
            break
    else:
        print("\nTable creation successful.")



def insert_values_to_table(table, values):
    try:
        cursr.execute(f'INSERT INTO {table} VALUES ({values})')
        print("\n Values successfully inserted.\n")
        conn_obj.commit()
        cursr.execute(f"SELECT * FROM {table}")
        res = cursr.fetchall()
        print(res)
    except Exception as e:
        print(f"Error occurred while inserting values: {e}")



def validate_input(string, regex_pattern):
    while True:
        if re.match(regex_pattern, string):
            return True
        else:
            return False


def validate_election_id(election_id, admin_id):
    cursr.execute(f"SELECT * FROM ELECTION WHERE election_id={election_id} AND ADMINID={admin_id}")
    res = cursr.fetchall()
    return True if res else False


# def update_posts(post_id, election_id):
#     cursr.execute(f"UPDATE POSTS SET NO_OF_CANDIDATES = NO_OF_CANDIDATES + 1 WHERE POST_ID = {post_id} AND ELECTIONID = {election_id}")
#     print('Posts_updated')



def insert_admin_values():
    department = validate_input("Enter department: ", r'^[A-Za-z]{1,5}$')
    name = validate_input("Enter name: ", r'^[A-Za-z ]{1,30}$')
    admin_id = validate_input("Enter admin ID: ", r'^\d+$')
    phone = validate_input("Enter phone (10 digits): ", r'^\d{10}$')
    passwd = getpass.getpass("Enter your password: ")
    pass_bytes = passwd.encode('utf-8')
    passwd = hashlib.sha256(pass_bytes).hexdigest()
    insert_values_to_table('ADMIN', f'\"{department.upper()}\", \"{name}\", {admin_id}, \"{phone}\", \"{passwd}\" ')


def insert_election_values(admin_id,year,election_id):
    # year = validate_input("Enter election year: ", r'^\d{4}$')
    # if int(year) <= datetime.date.today().year:
    #     return
    # election_id = validate_input("Enter election ID: ", r'^\d+$')
    # admin_id = validate_input("Enter admin ID: ", r'^\d+$')
    insert_values_to_table("ELECTION", f' {year}, {election_id}, {admin_id}')


def insert_posts_values():
    # no_of_candidates = validate_input("Enter number of candidates: ", r'^\d+$')
    post_id = validate_input("Enter post ID: ", r'^\d+$')
    election_id = validate_input("Enter election ID: ", r'^\d+$')
    post_name = validate_input("Enter post name: ", r'^[A-Za-z]{1,15}$')
    insert_values_to_table("POSTS", f'0, {post_id}, {election_id}, \"{post_name}\"')
    

def insert_voters_values():
    usn = validate_input("Enter USN (10 characters): ", r'^[A-Za-z0-9]{10}$')
    department = validate_input("Enter department: ", r'^[A-Za-z]{1,5}$')
    name = validate_input("Enter name : ", r'^[A-Za-z ]{1,30}$')
    phone = validate_input("Enter phone (10 digits): ", r'^\d{10}$')
    email = validate_input("Enter email: ", r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    semester = validate_input("Enter semester: ", r'^\d{1}$')
    passwd = getpass.getpass("Enter your password: ")
    pass_bytes = passwd.encode('utf-8')
    passwd = hashlib.sha256(pass_bytes).hexdigest()
    try:
        insert_values_to_table("VOTERS",f'\"{usn.upper()}\", \"{department.upper()}\", \"{name}\", \"{phone}\", \"{email}\", {semester}, \"{passwd}\"')
        print("Sign up successfully completed. Please go back to login.")
    except:
        print("Voter already exists. Please Log In.")


def insert_candidates_values(admin_id):
    usn = validate_input("Enter USN (10 characters): ", r'^[A-Za-z0-9]{10}$')
    semester = validate_input("Enter semester: ", r'^\d{1}$')
    post_id = validate_input("Enter post ID: ", r'^\d+$')
    department = validate_input("Enter department: ", r'^[A-Za-z0-9]{1,5}$')
    name = validate_input("Enter name: ", r'^[A-Za-z0-9 ]{1,30}$')
    phone = validate_input("Enter phone (10 digits): ", r'^\d{10}$')
    email = validate_input("Enter email: ", r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    election_id = validate_input("Enter election ID: ", r'^\d+$')
    gender = validate_input("Enter gender (M/F): ", r'^[MFmf]$')

    if validate_election_id(election_id, admin_id):
        insert_values_to_table("CANDIDATES", f'\"{usn.upper()}\", {semester}, {post_id},\"{department.upper()}\", \"{name}\", \"{phone}\", \"{email}\", {election_id}, \"{gender}\"')
        # update_posts(post_id,election_id)
    else:
        print("You cannot add Candidate to other admin's election.")


def show_elections(admin_id):
    cursr.execute(f"SELECT * FROM ELECTION WHERE ADMINID={admin_id} ORDER BY YEAR")
    res = cursr.fetchall()
    for i in res:
        print("Election ID: ", i[1])
        print("Year: ", i[0])


def show_election_details(admin_id, election_id):
    cursr.execute(f"SELECT * FROM ELECTION WHERE ADMINID={admin_id} ORDER BY YEAR")
    res = cursr.fetchall()
    if res:
        for i in res:
            print("Election ID: ", i[1])
            print("Year: ", i[0])
            cursr.execute(f"SELECT POST_ID, NO_OF_CANDIDATES, POSTNAME FROM POSTS WHERE ELECTIONID={election_id} ORDER BY POST_ID")
            res1 = cursr.fetchall()
            print("Posts: ")

            myTable = PrettyTable(["Post ID", "No. of Candidates", "Post Name"])
            for i in res1:
                myTable.add_row(i)
            return myTable, i[0]

            # for j in res1:
            #     print("No. of Candidates \t Post ID \t Post Name")
            #     print("\t "+str(j[0])+" \t \t "+str(j[2])+" \t "+j[3])
    else:
        print("Empty Set.")



def show_election_candidates(election_id):
    cursr.execute(f"SELECT * FROM CANDIDATES WHERE ELECTIONID={election_id}")
    # cursr.execute(f"SELECT * FROM CANDIDATES WHERE ELECTIONID IN (SELECT ELECTION_ID FROM ELECTION WHERE ELECTION_ID={election_id} AND ADMINID={admin_id}) ")
    res = cursr.fetchall()
    if res:
        myTable = PrettyTable(["USN","SEMESTER", "POSTID", "DEPARTMENT", "NAME", "PHONE", "EMAIL", "ELECTIONID", "GENDER"])
        for i in res:
            myTable.add_row(i)
        return myTable
    else:
        return None


def remove_candidate(admin_id):
    usn = validate_input("Enter USN to remove(10 characters): ", r'^[A-Za-z0-9]{10}$')
    cursr.execute(f"SELECT * FROM CANDIDATES WHERE USN = {usn} AND ELECTIONID IN (SELECT ELECTION_ID FROM ELECTION WHERE ADMINID={admin_id})")
    res = cursr.fetchall()
    if res:
        try:
            cursr.execute(f"DELETE FROM CANDIDATES WHERE USN = '{usn}'")
            print("Candidate removed successfully.")
        except:
            print("USN not found.")
    else:
        print("You cannot delete candidate from other Admin's elections.")


def login_admin(id, password):
    pass_bytes = password.encode('utf-8')
    password = hashlib.sha256(pass_bytes).hexdigest()
    # cursr.execute(f"SELECT * FROM ADMIN WHERE PASSWD=\'{password}\' AND  ADMIN_ID IN (SELECT ADMIN_ID FROM ADMIN WHERE ADMIN_ID ={id}")
    cursr.execute(f"SELECT * FROM ADMIN WHERE ADMIN_ID=\'{id}\' AND PASSWD=\'{password}\'")
    result = cursr.fetchall()

    if not result:
       print("Login failed. Check your credentials and retry.")
       return None,None
    else:
        print("Login successful.")
        return result[0][1], result[0]


def login_voter(id, password):
    pass_bytes = password.encode('utf-8')
    password = hashlib.sha256(pass_bytes).hexdigest()
    # cursr.execute(f"SELECT * FROM VOTERS WHERE PASSWD=\'{password}\' AND  USN IN (SELECT USN FROM VOTERS WHERE USN=\'{id}\'")
    cursr.execute(f"SELECT * FROM VOTERS WHERE USN=\'{id}\' AND PASSWD=\'{password}\'")
    result = cursr.fetchall()

    if not result:
       print("Login failed. Check your credentials and retry.")
       return None,None
    else:
        print("Login successful.")
        return result[0][2], result[0]


def generate_bar_graph(candidates, total_votes, election_id, post_id):
    fig = plt.figure(figsize=(10, 6))
    plt.bar(candidates, total_votes, color='blue')
    plt.legend()
    plt.xlabel('Candidate ID')
    plt.ylabel('Total Votes')
    plt.title(f'Results for Post {post_id} of Election {election_id}')
    plt.savefig(f'results/bar_e{election_id}_p{post_id}.png')
    plt.show()


def generate_pie_chart(candidates, total_votes, election_id, post_id):
    # fig = plt.figure(figsize=(10, 6))
    # plt.pie(total_votes, labels=candidates, autopct='%1.1f%%', startangle=120)
    # plt.axis('equal')
    # plt.title('Percentage of Votes for Each Candidate')
    # plt.savefig(f'results/pie_e{election_id}_p{post_id}.png')
    # plt.show()

    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = ax.pie(total_votes, labels=candidates, autopct='%1.1f%%', startangle=120)
    ax.legend(wedges, candidates, title='Candidates', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title(f'Results for Post {post_id} of Election {election_id}')
    plt.savefig(f'results/pie_e{election_id}_p{post_id}.png')

    # Show the plot
    plt.show()


def generate_result(election_id, plot_choice):
    cursr.execute(f"SELECT DISTINCT POSTID FROM VOTE_COUNT WHERE ELECTIONID={election_id}")
    res = cursr.fetchall()
    if res:
        cursr.execute(f"SELECT POST_ID FROM POSTS WHERE ELECTIONID={election_id}")
        posts = cursr.fetchall()
        for i in posts:
            cursr.execute(f"SELECT CANDIDATEID, TOTAL_VOTES FROM VOTE_COUNT WHERE POSTID={i[0]} AND ELECTIONID={election_id}")
            votes = cursr.fetchall()
            candidates = [row[0] for row in votes]
            total_votes = [row[1] for row in votes]
            if plot_choice==1:
                generate_bar_graph(candidates,total_votes, election_id, i[0])
            else:
                generate_pie_chart(candidates, total_votes, election_id, i[0])






# if __name__ == '__main__':
#     dbms_connect('')
#     create_database()
#     while True:
#         print("\nWelcome to Voting System!!!\n")
#         choice = int(input("1. LOGIN \n2. SIGN UP \n3. EXIT \nEnter your response: "))
#         if choice == 1:
#             choice2 = int(input("\nLogin as: \n1. ADMIN \n2. VOTER \nEnter your response:"))
#             if choice2 == 1:
#                 print("\nPlease enter the following required parameters: ")
#                 id = int(input("Enter Admin ID: "))
#                 passwd = getpass.getpass("Enter Password: ")
#                 name, user_data = login_admin(id, passwd)
#                 if name:
#                     print("\nWelcome ",name)
#                     while(True):
#                         print("\nSelect what you want to do: \n")
#                         choice3 = int(input("1. Create a new Election \n2. View all Elections \n3. View Candidates of a election \n4. View Election details \n5. Make changes in a Election \n6. Generate Election Results \n7. LOG OUT \nEnter your response: "))
#                         if choice3 == 1:
#                             insert_election_values(user_data[2])
#                         elif choice3 == 2:
#                             show_elections(user_data[2])
#                         elif choice3 == 3:
#                             election_id = validate_input("Enter election ID to view Candidates: ", r'^\d+$')
#                             show_election_candidates(election_id,)
#                         elif choice3 == 4:
#                             election_id = validate_input("Enter election ID to view details: ", r'^\d+$')
#                             if election_id:
#                                 show_election_details(user_data[2],election_id)
#                         elif choice3 == 5:
#                             while True:
#                                 print("\nSelect what change you want to do: \n")
#                                 choice4 = int(input("1. Add Candidate \n2. Remove Candidate \n3. Change year of election \n4. Add a Post \n5. GO BACK \nEnter your response: "))
#                                 if choice4 == 1:
#                                     insert_candidates_values(user_data[2])
#                                 elif choice4 == 2:
#                                     remove_candidate(user_data[2])
#                                 elif choice4 == 3:
#                                     election_id = validate_input("Enter election ID: ", r'^\d+$')
#                                     year = validate_input("Enter election year: ", r'^\d{4}$')
#                                     if year <= datetime.today().year:
#                                         print("\nEnter a valid election year.")
#                                     else:
#                                         cursr.execute(F"UPDATE ELECTION SET YEAR={year} WHERE ELECTION_ID={election_id}")
#                                 elif choice4 == 4:
#                                     insert_posts_values()
#                                 elif choice4 == 5:
#                                     break
#                                 else:
#                                     print("Pleease enter a valid input.")
#                         elif choice3 == 6:
#                             cursr.execute(f"SELECT ELECTION_ID FROM ELECTION WHERE ADMINID={user_data[2]} AND ELECTION_ID IN (SELECT DISTINCT ELECTIONID FROM VOTE_COUNT)")
#                             elections = cursr.fetchall()
#                             if elections:
#                                 print("\nSelect the election to generate Results:")
#                                 for i in range(len(elections)):
#                                     print(str(i+1)+".",elections[i][0])
#                                 election_id = elections[int(input("Enter your response: "))-1][0]
#                                 plot_choice = int(input("\nWhat type of Result you want to generate? \n1. Bar Graph \n2. Pie Chart \nEnter your response: "))
#                                 generate_result(election_id, plot_choice)

#                         elif choice3 == 7:
#                             break                      
#                         else:
#                             print("Invalid input.")
#                 else:
#                     print("Login Unsuccessful. \nPlease Retry")
#                     break
            
            
#             elif choice2 == 2:
#                 print("\nPlease enter the following required parameters: ")
#                 id = validate_input("Enter USN (10 characters): ", r'^[A-Za-z0-9]{10}$')
#                 if id:
#                     passwd = getpass.getpass("Enter Password: ")
#                     name, user_data = login_voter(id, passwd)
#                     if name:
#                         print("\nWelcome ",name)
#                         while True:
#                             choice3 = int(input("\n1. Vote in a election \n2. Log Out \nEnter your response: "))
#                             if choice3 ==1:
                                
#                                 cursr.execute(f"SELECT ELECTION_ID FROM ELECTION WHERE YEAR>={datetime.datetime.now().year}")
#                                 elections = cursr.fetchall()
#                                 for i in range(len(elections)):
#                                     print(str(i+1)+".",elections[i][0])
#                                 choice4 = int(input("Select the election you want to vote in: "))
#                                 vote_in_election = elections[choice4-1][0]
#                                 print(vote_in_election)
#                                 cursr.execute(f"SELECT POST_ID, POSTNAME FROM POSTS WHERE ELECTIONID={vote_in_election}")
#                                 posts = cursr.fetchall()
#                                 cursr.execute(f"SELECT VOTERID FROM VOTES WHERE ELECTIONID={vote_in_election} AND VOTERID=\'{user_data[0]}\'")
#                                 temp=cursr.fetchall()
#                                 if not temp:
#                                     for i in posts:
#                                         print()
#                                         print("Vote for: ")
#                                         print("POST ID: ", i[0])
#                                         print("POST NAME: ", i[1])
#                                         cursr.execute(f"SELECT USN, NAME FROM CANDIDATES WHERE ELECTIONID={vote_in_election} AND POSTID={i[0]}")
#                                         candidates = cursr.fetchall()
#                                         for j in range(len(candidates)):
#                                             print(str(j+1)+".", candidates[j][0], candidates[j][1])
#                                         while True:
#                                             vote = int(input("Enter your vote: "))
#                                             if vote<=len(candidates):
#                                                 try:
#                                                     print(f"INSERT INTO VOTES VALUES (\'{user_data[0]}\', {vote_in_election}, {i[0]}, \'{candidates[vote-1][0]}\')")
#                                                     cursr.execute(f"INSERT INTO VOTES VALUES (\'{user_data[0]}\', {vote_in_election}, {i[0]}, \'{candidates[vote-1][0]}\');")
#                                                     conn_obj.commit()
#                                                     print("Vote registered successfully")
#                                                     break
#                                                 except:
#                                                     print(f"INSERT INTO VOTES VALUES (\'{user_data[0]}\', {vote_in_election}, {i[0]}, \'{candidates[vote-1][0]}\')")
#                                                     print("Failed to register the vote.")
#                                             else:
#                                                 print("Please enter a valid vote.")
#                             elif choice3 ==2:
#                                 break
#                             else:
#                                 print("Enter a valid input.")
                                    
#                 else:
#                     break
            
#             else:
#                 print("Invalid response.")   

#         elif choice == 2:
#             choice2 = int(input("\nSign up as: \n1. ADMIN \n2. VOTER \nEnter your response:"))
#             if choice2 == 1:
#                 print("Please enter the following required parameters: ")
#                 insert_admin_values()
#                 print("Sign up successfully completed. Please go back to login.")

#             elif choice2 == 2:
#                 print("Please enter the following required parameters: ")
#                 insert_voters_values()
                

#             else:
#                 print("Invalid response.")

#         elif choice == 3:
#             break
#         else:
#             print("Please enter a valid choice:")
    
#     close_connection()



if __name__ == "__main__":
    dbms_connect('')
    create_database()
    root = tk.Tk()
    app = VotingSystemGUI(root)
    root.mainloop()
    close_connection()



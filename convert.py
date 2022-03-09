from datetime import datetime
import csv, os
from types import NoneType
import pandas as pd


def CheckBudgetCategory(array):
    #The Format of the array is [Date, Name of Store, $Amount, Account purchased from, Budget Category] 
    question = ["walmart", "amazon", "target", "big lots"]
    for row in array:
        # Checks if the account the item was bought from is the grocery account, appends "Grocery" in the  Budget category column.
        if row[3] == "Grocery":
            row[len(row) - 1] = "Grocery"
        
        # Checks if the Category of purchase is gas and less than $12, to change the category to "gas junk"
        if row[len(row) - 1].lower() == "gas" and float(row[2]) < 12.00:
            row[len(row) - 1] = "gas junk"

        # If the store name of entry in purchase array is in the "question array" above AND the account used to purchase IS
        #  NOT grocery, then prompt to change the budget category for that store name.
        if row[1].lower() in question and row[3] != "Grocery":
            print("")
            change = input("$" + str(row[2]) + " at " + row[1].upper() + " on " + row[0] + " is " + row[len(row) - 1].upper() +
            ". \nType to change budget category. Enter to keep >>> ").title()
            if change != "":
                row[len(row) - 1] = change

def CreatePurchases(*args):
    # This function initializes a blank array and then iterates through all supplied transaction
    # arrays to combine into one "Purchases" array
    purchases = []
    try:
        for each in args:
            for item in each:
                purchases.append(item)

        purchases = SortArray(purchases)

    except TypeError:
        pass

    return purchases

def ComparePurchases(new, old):
    new_purchase_list = []
    # Compares the old purchase list from a previous run of the program against a new purchase list of the current run
    # All items that have already been process in the old purchase array are currently in the new purchase array
    # so this function only produces an array of purchases that have not already been processed yet.
    for x in range(len(old),len(new)):
        new_purchase_list.append(new[x])

    return new_purchase_list

def DeleteFile(file):
    
    if os.path.isfile('Credit.csv') and os.path.isfile('Joint.csv') and os.path.isfile('Grocery.csv') == True:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

# This function is the workhorse of this program.
def Format(array):
    unwanted = [str(x) for x in range(0,10)]

    # Loops through the dollar values and appends a zero to the end of the dollar amounts to have $X.XX format.
    for row in array:
        try:
            # This line standardizes all numeric entries to be a string, and to absolute value.
            row[2] = str(float(str(row[2])) * -1)
            if row[2][-3] != ".":
                row[2] = row[2] + "0"

        except ValueError:
            pass
    
    # Changes the Vendor Code in the raw purchase array to be at most 10 characters, or until the first number is reached.
    # May run into problems if the Vendor Code on the raw purchase array either starts with numbers, or has numbers only a few (I'm guessing less 
    # than 3 characters would cause problems) characters in.
    for each in array:
        temp = ""
        for letters in each[1]:
            if letters not in unwanted and len(temp) < 10:
                temp += letters
            else:
                each[1] = temp
                break

    # This large block of code formats the purchase array to be the "plaintext" name of the store the purchase was made by comparing the edited (from 
    # the loop immediately above this) Vendor Code and matching it to the approved plaintext store name in the categories csv.
    for purchase in array:
        if purchase[1].lower() != "name":
            VCExists = False

            for entry in categories:

                #if Vendor code is already in list of vendor codes
                if purchase[1] in entry:

                    #change vendor code to Store name on the Purchases file
                    purchase[1] = entry[0]

                    #add the budget category
                    purchase.append(entry[1])

                    # Signals that the vendor code exists in the categories array.
                    VCExists = True
                    break
            
            # If the vendor code does not exist in any of the arrays in the categories array...
            if VCExists == False:
                newEntry = True
                # print(purchase[1] + " for $" + purchase[2] + " on " + purchase[0] + " from " + purchase[3])

                # Prints out the Store name, for X price, on Y date, from Z store.
                print(f"{purchase[1]} for ${purchase[2]} on {purchase[0]} from {purchase[3]}")

                # Prompts user for plaintext of the store's name.
                storeName = input("Name of Store? >> ").lower()

                # Loops through each array in the categories array.
                for each in categories:

                    # If the supplied plaintext name matches the plaintext store name of an array in the categories array...
                    if storeName == each[0].lower():

                        # Appends the abbv. VC to the list of VCs that are associated with that store name.
                        each.append(purchase[1])

                        # Changes the abbv. VC in the purchase array to the plaintext store name already in the categories array
                        purchase[1] = storeName

                        # Appends the Budget Category already designated in the categories array associated with that store
                        purchase.append(each[1])

                        # Signals that the Vendor Code now exists
                        VCExists = True

                        # Signals that a new entry into the categories array is not needed.
                        newEntry = False

                # If the plaintext store name is not in the categories array then...
                if newEntry == True:
                    # Initializes a new array to add to the categories array.
                    newArray = []

                    # Prompts the user for the budget category of this new store.
                    budgetCategory = input("Budget Category? >> ")

                    # Builds the new category array entry
                    newArray = [storeName,budgetCategory,purchase[1]]

                    # Attaches the new category array entry to the category array.
                    categories.append(newArray)

                    # Changes the abbv. VC in the purchase array to the plaintext store name.
                    purchase[1] = storeName

                    # Attaches the budget category to that purchase.
                    purchase.append(budgetCategory)
    
    # Titlizes all values in the now properly formatted purchase array.
    for row in array:
        for x in range(0,len(row)):
             row[x] = row[x].title()

def OpenFile(file):
    array = []
    try:
        with open(file, newline='') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                if row[0].lower() != 'Date':
                    row[0] = row[0].lower()
                    array.append(row)
                else:
                    array.append(row)
                    
    #Opens the categories or purchases CSV file. If no file exists then it inititalizes a header array for top of csv file.
    except FileNotFoundError:
        if file == 'categories.csv':
            array = [["Store Name", "Budget Category", "Vendor Code","Vendor Code","..."]]
            print("No Categories.csv file in Directory")

        if file == 'Purchases.csv':
            array = [["Date","Name","Amount","Account","Budget Category"]]
            print("No Purchases.csv file in Directory")
        
    return array

def OpenBankCSV(file):
    try:
        bank_array = []
        with open(file, 'r',newline='') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                new_array = []
                if row != [] and row[1] != "USAA Transfer" and row[0] != "forecasted" and row[0] != "Date":
                    for item in row:
                        # Skips empty values that are in each row of the csv file.
                        if (item != ""):
                            new_array.append(item.lower())
                    bank_array.append(new_array)

                if 'Joint.csv' in file:
                    new_array.append("Joint Checking")

                if 'Grocery.csv' in file:
                    new_array.append("Grocery")

            # removes unnessary values, such as codes that the bank uses to distinguish purchases, from the bank_array
            for row in bank_array:
                del row[2]
                del row[2]
                del row[3]

                # Formats the date value to MM/DD/YYYY
                row[0] = datetime.strftime(datetime.strptime(row[0], '%Y-%m-%d'), '%m/%d/%Y')
            
            for row in bank_array:
                if "payroll" in row[1].lower():
                    row[1] = "income"
                    row[2] = "-" + row[2]
                if "ameritrade" in row[1].lower():
                    row[1] = "td ameritrade"

            return bank_array

    except FileNotFoundError:
        pass

def OpenCreditCSV(file):
    try:
        cc_array = []
        with open(file, 'r',newline='') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                new_array = []

                # Leaves off values in credit card statement that are payments to the credit card, or the header of the csv file.
                if row[2].lower() != "internet payment thank you" and row[0].lower() != 'date':
                    for item in row:
                        # Skips blank entries in each row of the csv file.
                        if (item != ""):
                            new_array.append(item.lower())

                    # Appends "Credit" into the "Account" position of the credit card array.
                    new_array.append("Credit")
                    cc_array.append(new_array)
            
            # Cleans up unneeded information from the credit card arrays.
            for row in cc_array:
                del row[1]
                del row[2]

                # Formats the date in each purchase to MM/DD/YYYY
                row[0] = datetime.strftime(datetime.strptime(row[0], '%Y-%m-%d'), '%m/%d/%Y')

            return cc_array

    except FileNotFoundError:
        pass

# Sorts the Purchase array by day in ascending order.
def SortArray(array):
    sorted = []
    for x in range(0,32):
        for each in array:
            if int(each[0][3] + each[0][4]) == x:
                sorted.append(each)
    return sorted

def UpdateCategories(array):
    with open('categories.csv','w', newline='') as writeFile:
        writer = csv.writer(writeFile,quoting=csv.QUOTE_MINIMAL)
        for item in array:
            for each in item:
                each = each.title()  
            writer.writerows([item])

def UpdatePurchases(array):
    old = OpenFile('Purchases.csv')

    for each in array:
        if each not in old:
            old.append(each)
    
    # Writes updated purchases file
    if old[0] != ["Date","Name","Amount","Account","Budget Category"]:
        old.insert(0,["Date","Name","Amount","Account","Budget Category"])

    with open('Purchases.csv','w',newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(old)
    
if __name__ == "__main__":

    os.system("cls")
    categories = OpenFile('categories.csv')
    oldPurchases = CreatePurchases(OpenCreditCSV('OldCredit.csv'),OpenBankCSV('OldJoint.csv'),OpenBankCSV('OldGrocery.csv'))
    newPurchases = CreatePurchases(OpenCreditCSV('Credit.csv'),OpenBankCSV('Joint.csv'),OpenBankCSV('Grocery.csv'))
    newList = ComparePurchases(newPurchases, oldPurchases)
    
    Format(newList)
    CheckBudgetCategory(newList)

    UpdateCategories(categories)
    UpdatePurchases(newList)
    
    # Deletes the old account statements 
    DeleteFile('OldCredit.csv')
    DeleteFile('OldJoint.csv')
    DeleteFile('OldGrocery.csv')

    # Then renames the current account statements as the old account statements, in order to prime the next use of the program.
    try:    
        os.rename(r'Credit.csv', r'OldCredit.csv')
        os.rename(r'Joint.csv', r'OldJoint.csv')
        os.rename(r'Grocery.csv', r'OldGrocery.csv')

    except FileNotFoundError:
        print("No New Account statements to rename as old.")
        pass

    # Writes the Purchases list to an excel sheet
    read_file = pd.read_csv (r'Purchases.csv')
    read_file.to_excel (r'Purchases.xlsx', index = None, header = False)
    
    # Opens the Purchases excel sheet
    # Use this for Windows

    os.system("start EXCEL.EXE Purchases.xlsx")

    # # # Use this for Mac
    # # os.system("open -a 'Microsoft Excel.app' 'Purchases.xlsx'")
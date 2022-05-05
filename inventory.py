import sys
import os
import re
import json
import string

file = "inventory.json"

class Item:
    def __init__(self, name="", ASIN="", FNSKU="", keys = [], retail=0, quantity=0):
        self.name = name
        self.ASIN = ASIN
        self.FNSKU = FNSKU
        self.keys = keys
        self.retail = retail
        self.quantity = quantity
        self.listing = "https://amazon.com/dp/" + ASIN
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        
    def print(self):
        print("Item: " + self.name)
        print("ASIN: " + self.ASIN)
        print("FNSKU: " + self.FNSKU)
        if(len(self.keys) == 1):
            print("Key: " + self.keys[0])
        else:
            keyString = ""
            for k in self.keys:
                keyString += k + ", "
            keyString = keyString[:-2]
            print("Keys: " + keyString)
        print("Retail: " + str(self.retail))
        print("Quantity: " + str(self.quantity))
        print("----------------------------------")
        
class Inventory:
    def __init__(self, items=None):
        if items is None:
            self.items = []
        else:
            self.items = items
    
    def add(self, item):
        self.items.append(item)
    
    def print(self):
        counter = 0
        print("----------------------------------")
        for i in self.items:
            i.print()
            counter += 1
        if counter == 0:
            print("No items found!")
            print("----------------------------------")
    
    
    def toJSON(self):
        return json.dumps(self.items, default=lambda o: o.__dict__, sort_keys=True)
    
def clearScreen():
    if(os.name == "posix"):
        _ = os.system("clear")
    else:
        _ = os.system("cls")
    
def searchIndex(inventory, key):
    j = 0
    for i in inventory.items:
        if(i.ASIN == key or i.FNSKU == key or key in i.keys):
            return j
        else:
            j += 1
   
    # If not returned by now, no key found
    return -1

def saveInventory(inventory):
    with open(file, "w") as f:
        f.write(inventory.toJSON())
        f.close()

def loadInventory():
    with open(file, "r") as f:
        data = json.load(f)
        f.close()
        
    loadedInventory = Inventory()
    for i in data:
        item = Item(i["name"], i["ASIN"], i["FNSKU"], i["keys"], i["retail"], i["quantity"])
        loadedInventory.add(item)
    return loadedInventory
    
def inputMode(inventory):
    while(True):
        inventory = loadInventory()
        print("Input Menu")
        print("1 : Rapid Mode - No extra details")
        print("2 : Detailed Mode - Input all details")
        print("0 : Back to Main Menu")
        option = input("Menu Choice: ")
        
        match option:
            case "0":
                clearScreen()
                break
            case "1":
                print("Input 0 for Key when finished")
                while(True):
                    scan = input("Scan Key: ")
                    if scan == "0" :
                        clearScreen()
                        break
                    else: 
                        index = searchIndex(inventory, scan)
                        if(index == -1):
                            if(scan[0] == "X"):
                                inventory.add(Item("", "", scan, [], 0, 1))
                            elif(scan[0] == "B"):
                                inventory.add(Item("", scan, "", [], 0, 1))
                            else:
                                inventory.add(Item("", "", "", [scan], 0, 1))
                            saveInventory(inventory)
                        else: 
                            inventory.items[index].quantity += 1
                            saveInventory(inventory)

            case "2":
                print("Input 0 for Key when finished")
                while(True):
                    scan = input("Scan Key: ")
                    if scan == "0" :
                        clearScreen()
                        saveInventory(inventory)
                        break
                    else: 
                        clearScreen()
                        print("Scan Key: " + scan)
                        index = searchIndex(inventory, scan)
                        if(index == -1):
                            name = input("Item Name: ")
                            if(scan[0] == "X"):
                                ASIN = input("Item ASIN: ")
                            elif(scan[0] == "B"):
                                FNSKU = input("Item FNSKU: ")
                            else:
                                ASIN = input("Item ASIN: ")
                                FNSKU = input("Item FNSKU: ")
                            while(True):
                                retail = input("Item Retail Price: $")
                                try:
                                    retail = round(float(retail), 2)
                                    break
                                except ValueError:
                                    print("Invalid input!")
                            while(True):
                                quantity = input("Item Quantity: ")
                                if(quantity.isdigit()):
                                    quantity = int(quantity)
                                    break
                                else:
                                    print("Invalid input!")
                                    
                            if(scan[0] == "X"):
                                inventory.add(Item(name, ASIN, scan, [], retail, quantity))
                            elif(scan[0] == "B"):
                                inventory.add(Item(name, scan, FNSKU, [], retail, quantity))                                                                     
                            else:
                                inventory.add(Item(name, ASIN, FNSKU, [scan], retail, quantity))
                                
                            clearScreen()
                            print("----------------------------------")
                            print("Item Added!")
                            print("----------------------------------")
                            saveInventory(inventory)
                        else:
                            inventory.items[index].quantity += 1
                            clearScreen()
                            print("----------------------------------")
                            print("Item already exists, increasing quantity!") 
                            print("Use edit mode to change details")
                            print("----------------------------------")
                            saveInventory(inventory)
                            

def outputMode(inventory):
    print("Input 0 for Key when finished")
    while(True):
        scan = input("Scan Key: ")
        if scan == "0" :
            clearScreen()
            break
        else: 
            index = searchIndex(inventory, scan)
            if(index == -1):
                print("Item not found")
            else: 
                if(inventory.items[index].quantity > 0):
                    inventory.items[index].quantity -= 1
                    if(inventory.items[index].quantity == 0):
                        print("WARNING - That is the last item in inventory")
                elif(inventory.items[index].quantity == 0):
                    print("ERROR - Invalid quantity of items in stock")
                    print("ERROR - Quantity would be negative")
                saveInventory(inventory)

def searchMode(inventory):
    while(True):
        print("Input 0 for Key when finished")
        scan = input("Scan Key: ")
        if(scan == "0"):
            clearScreen()
            break
        else:
            index = searchIndex(inventory, scan)
            if(index == -1): 
                print("Item not found")
            else:
                print("----------------------------------")
                inventory.items[index].print()

def editMode(inventory):
    while(True):
        print("Input 0 for Key when finished")
        scan = input("Scan Key: ")
        if(scan == "0"):
            clearScreen()
            break
        else:
            index = searchIndex(inventory, scan)
            if(index == -1): 
                print("Item not found")
            else:
                # variables to revert edit in the case of no identifiers
                oldName = inventory.items[index].name
                oldASIN = inventory.items[index].ASIN
                oldFNSKU = inventory.items[index].FNSKU
                oldKeys = inventory.items[index].keys
                oldRetail = inventory.items[index].retail
                oldQuantity = inventory.items[index].quantity
                
                print("----------------------------------")
                print("Input # for no change")
                
                # Change name
                print("Current Name: " + inventory.items[index].name)
                change = input("New Name: ")
                if(change != "#"):
                    inventory.items[index].name = change
                    
                # Change ASIN
                print("Current ASIN: " + inventory.items[index].ASIN)
                change = input("New ASIN: ")
                if(change != "#"):
                    inventory.items[index].ASIN = change
                    inventory.items[index].listing = "https://amazon.com/dp/" + change
                    
                # Change FNSKU
                print("Current FNSKU: " + inventory.items[index].FNSKU)
                change = input("New FNSKU: ")
                if(change != "#"):
                    inventory.items[index].FNSKU = change
                  
                # Change keys
                if(len(inventory.items[index].keys) == 1):
                    print("Current Key: " + inventory.items[index].keys[0])
                else:
                    keyString = ""
                    for k in inventory.items[index].keys:
                        keyString += k + ", "
                    keyString = keyString[:-2]
                    print("Current Keys: " + keyString)
                print("Input comma separated with no spaces")
                print("(Old keys will be removed)")
                change = input("New Key(s): ")
                if(change != "#"):
                    formatted = re.sub(r"\s+", "", change)
                    keys = formatted.split(",")
                    keys = list(filter(None, keys))
                    inventory.items[index].keys = keys
                # Change retail price
                while(True):
                    print("Current Retail Price: $" + str(inventory.items[index].retail))
                    change = input("New Retail Price: $")
                    if(change != "#"):
                        try:
                            change = round(float(change), 2)
                            inventory.items[index].retail = change
                            break
                        except ValueError:
                            print("Invalid input!")
                    else:
                        break
                        
                # Change quantity
                while(True):
                    print("Current Quantity: " + str(inventory.items[index].quantity))
                    change = input("New Quantity: ")
                    if(change != "#"):
                        if(change.isdigit()):
                            inventory.items[index].quantity = int(change)
                            break
                        else:
                            print("Invalid input!")
                    else:
                        break
                        
                # Check if there are still identifiers
                if((inventory.items[index].ASIN.isspace() or inventory.items[index].ASIN == "") and (inventory.items[index].FNSKU.isspace() or inventory.items[index].FNSKU == "") and (len(inventory.items[index].keys) == 0 or inventory.items[index].keys[0] == "")):
                    print("Changes are not permitted since there would be no identifiers")
                    print("Reverting changes")

                    inventory.items[index].name = oldName
                    inventory.items[index].ASIN = oldASIN
                    inventory.items[index].FNSKU = oldFNSKU
                    inventory.items[index].keys = oldKeys
                    inventory.items[index].retail = oldRetail
                    inventory.items[index].quantity = oldQuantity
                    inventory.items[index].listing = "https://amazon.com/dp/" + oldASIN
                clearScreen()
                print("----------------------------------")
                print("Item Edited!")
                print("----------------------------------")
                saveInventory(inventory)
    
# Check for json and initialize of not present    
f = open(file, "a+")
f.close()    
if(os.stat(file).st_size == 0):
    f = open(file, "w")
    f.write("[]")
    f.close()

    
# main menu
while(True):
    inventory = loadInventory()
    print("DrowningWhale's Inventory Manager V1")
    print("Main Menu")
    print("1 : Input Mode")
    print("2 : Output Mode")
    print("3 : Search Mode")
    print("4 : Edit Mode")
    print("5 : Print Inventory")
    print("6 : Erase Inventory")
    print("0 : Exit")
    option = input("Menu Choice: ")
    option = option[0]
    clearScreen()
    
    match option:
        case "0": 
            break
        case "1":
            inputMode(inventory)
        case "2":
            outputMode(inventory)
        case "3":
            searchMode(inventory)
        case "4":
            editMode(inventory) 
        case "5":
            inventory.print()
        case "6":
            print("If you're sure that you want to erase your inventory file, type 'i am sure'")
            sure = input()
            if(sure == "i am sure"):
                with open(file, "w") as f:
                    f.write("[]")
                    f.close()

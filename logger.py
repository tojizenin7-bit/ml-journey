#logger.py - handles the daily logging flow
#this file contains all the logic for collectnh user input
#and passing it to storage.py to save
#separation of concerns as logger.py does not know how data is stored it just collects and validates it.
#storage.py does the saving this makes each file easy to test and modify independently

from datetime import date
#date.today() gives todays date as a date object
import storage 
#our own storage model , nptice no .py extension because its not a library but our own code


#the list of habits the app tracks
#storting it here means that you can constantly remove oradd habits- just edit the list npthing breaks

HABITS = ["excersise", "water(2L+)", "SLEEP(7+hrs)", "meditation", "reading", "no junk food"]

def log_today():
        """
    main function: walk the user through logging their day interactively.
    'interactive' means the program asks questions and waits for inputs.
    we use pythons built in input() function for this.
    """

        today = date.today().isoformat()
    #date.today() is date object like 2024-06-01
    #isoformat() converts it to string like "2024-06-01"
    #we store dates as strings beacuse SQLite has no native data type.

        print(f"\n logging entry for: {today}")
        print("-"*40)
    #the '-'*40 trick repeats the string '-' 40 times to create a visual separator in the console output
    #check for duplicate entry for today
    # we dont want the user to log on twice
        existing = storage.fetch_entry_by_date(today)
        if existing:
    #existing is a row object if an entry for today already exists, otherwise its None
            print(f"you have already logged today! Mood was{existing['mood']}/10.")
        overwrite = input("overwrite? (y/n)").strip().lower()
    #.strip() removes  leading/trailing whitespaces(spaces, newlines)
    #.lower() converts to lowercase so that "Y" and "y" both work

        if overwrite != "y":
            print("logging cancelled")
        return
    #exit the function ,no more code runs below this.
    #collect mood score
        mood = _get_integer_input(" mood (1-10):",1, 10)

    #collect energy score
        energy = _get_integer_input("energgy (1-10):", 1, 10)
    #collect free text note
        print("daily note(press enter to skip):", end="")
# end "" keeps the cursor on the same line as the prompt
        note = input().strip()
#collect habit comepletion
        print("\n Habits - did you do these today? (y/n)")
        habits ={}
#empty dictionary we will fill it below

        for habit in HABITS:
#loops through each habit string in our HABITS list
            answer = input(f"{habit}? (y/n):").strip().lower()
        habits[habit] = (answer == "y")
# (answer == "y") evaluates to True or False
#we store it in the dictionary with habit name as key

#summary feedback
        done_count = sum(1 for v in habits.values() if v)
#genrator expression inside sum() a compact way to count true values
#sum (i forf v in habits.values() if v)-> adds 1 for each habit where v id True
        print(f" completed {done_count}/{len(HABITS)} habits today .")
def _get_integer_input(prompt: str, min_val: int, max_val: int)-> int:
        """
        asks the user for a integer and keeps asking until they give a valid one.
        the leading underscore (_get_integer_input) is a python convention meaning
        "this is a private/internal helper funvtion - not meant to be called from outside this module."
        the while  True loop is the classic pattern for input validation:
        keep looping until the user gives you something valid, then break out. """
        while True:
            try:
                #try/except catches errors so the program doesnt crash.
                value = int(input(prompt))
        #int input ((..)) tries to convert the users text into a valid integer.
        # if the user enters "abc", int() raises a  Valueerror - caught below
                if min_val <= value <= max_val:
            #chained comparison python allows this , more readable than:
            #if value>=min_val and value<= max_val:
                    return value
        #valid input - exit the loop and return the number
                else:
                    print(f"please enter a number between{min_val} and {max_val}.")
            except ValueError:
#this block runs only if int(input(...)) failed (non-numeric input).
                print("Thats not a number. Try again.")

              
                  


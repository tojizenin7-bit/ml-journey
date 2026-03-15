#analyzer .py - crunches your lggedd data into insghts

#this is where the intelligence of the lifelog lives.
#we will learn : list comprehension, sorting, string processing, basic statistics, and working with pandas Dataframes.


import storage #our database layer
from collections import Counter #built in : counts occurences in list
import re  #regular expression for text processing
#try to import pandas
#we wrap the import in a try/exept as the app doesnt crash
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except  ImportError:
    PANDAS_AVAIOABLE = False
    print("pandas not installed. some analysis features will be limited.")
    print("Run : pip install pandas")

def get_mood_trend(entries: list) -> dict:
    """
    calculates moos statistics across all entries.
    return a dict with : avreage , highest, lowest, and the trend
    (are things getting better or worse recently ?).
    
    Parameters:
    entries- list of all sqlite3. Row oobjects from storage.fetch_all_entries()
    returns:
    dict with keys: avg, high, low, trend_direction """
    if not entries:
        # guard clause - if  the list is empty, return immediatley.
        #this prevents zerodivission error and other issues below
        return {}
    #list comprehension : builds a  new list from an iterable in one line
    #[expression for item in iterable] - very common in python
    moods =[entry["moods"] for entry in entries]
    #this is equivalent to: moods =[]
    #for entry in entries: moods.append(entry["mood"])

    avg_mood = round(sum(moods) / len(moods), 2)
    #sum(moods). -> adds all numbes in the list
    #len(moods)  -> count of items
    # round(..., 2) -> rounds to 2 decimal places
    # # trend compare last 7 days to presvious 7 days
    # #slicing : list[start:stop] -> gets a portion of the list
    # #[-7:] -> last 7 items (negative index counts from the end
    # #[-14:-7]) -> items from 14th last to 7th last
    recent_7 = moods[-7:]
    previous_7 = moods[-14:-7]
    
    trend_direction = "stable"
    if len(recent_7) >= 3 and len(previous_7) >=3:
        recent_avg = sum(recent_7) / len(recent_7)
        previous_avg = sum(previous_7)/ len(previous_7)

        if recent_avg > previous_avg + 0.5:
            trend_direction ="improving ↑"
        elif recent_avg < previous_avg - 0.5:
            trend_direction = "declining ↓"

    return {
        "avg":      avg_mood,
        "high":    max(moods),
        "low":     min(moods),
        "trend_direction":   trend_direction,
        "total_entries":     len(entries),
    }
def get_habit_stats(entries: list)-> dict:
    """ calculates completion streak of each habit and current streak for each.
    
        returns a dict: {habit_name {"rate": float, "streak": int}}
        """
    if not entries:
        return{}
    # we willl build a structure: {habir_name [True, false, true...]}
    #each list contains done/not-done values for each entry in date order
    habit_history = {}
    for entry in entries:
        entry_habits = storage.fetch_habits_for_entry(entry["id"])
    #for eac entry , fetch its linked hbaits from the habits table
    for h in entry_habits:
        name =h["name"]
        done = bool(h["done"])
        #convert 0/1 back to false/true
        if name not in habit_history:
            habit_history[name] =[]
            habit_history[name].append(done)
            #calculate rate + streak for each habit
            stats ={}
            for habit_name, history in habit_history.items():
                #.items() iterates key value pairs of a doctionary
                # completion rate: count of true values or total entries
                rate = round(sum(history)) /len(history* 100, 1) 
        # 100 * converts the 0.7 to 70.0 (percentage)
        # current streak: count backwards from today streak =0
        for did_it in reversed(history):
            #reversed( ) iterates a list backwards without copying it
            if did_it :
                streak += 1
            else:
                break #stop as soon as we hit missed day
            #'break' exits the for loop immediately
            stats[habit_name] ={"rate": rate, "streak": streak}
            return stats
def get_word_frequency(entries: list, top_n: int = 15) -> list:
    """
    analyses all journal notes and returns the most common meaningful words.
    this NLP natural lanuguage processing finds patterns in text
    returns a list of (word, count) tuples, sorted by count descending."""

    #words to ignore are clled stop words in NLP
    #sets are included to check instead of list for stop words
    # word in STOP WORDS is 0(1) for sets vs 0(n) for lists very importnat for large data sets
    all_words = []
    for entry in entries:
        note = entry["note"] or ""
        #'or ""' handles the case where note is none (not set).
        # in python: None or "" returns "" (the non falsy right side)
        # #re.findall() uses a regex pattern to extract all matching substrings.
        # r'\b[a-zA-Z]{3,}\b means:
        # \b: word boundary  (start/end o
        #f a word) [a-zA-Z]: anyletter(a-z or A-Z) {3,}: 3 or more characters 
        # .lower() normalises "Good" and "good" to the same word
        # filter out stop words using a list comprehension with a condition:
        # [expression for item in iterable if condition]  
        filtered = [w for w in words if w not in STOP_WORDS]
        all_words.extend(filtered)
        #.extend() adds all items from filtered into all_words
        # (unlike .append )which would add the list as a single item 
        if not all_words:
         return[]
        #counter is a special dictionary that counts occurences
        #({"cat": 2, "dog": 1})
        counter = counter(all_words)

        #.most_common(n) returns n most frequent items as [(word, count),....]
        return counter.most_common(top_n)
def get_mood_vs_habits_correlation(entries: list) -> list:
    """finds which habits correlate most with higher mood scores.
    correlation: when a habit X is done, is the mood score typically higher?
    this is a simplified correlation- not statisticallyrigorous, but useful.
    
    returns a list of dictssorted by mood impact (highest first)"""

    habit_mood_with = {} #mood scores on days habit was done
    habit_mood_without = {} #mood scores on days habit was not done   
    for entry in entries:
        mood = entry["mood"]
        habits = storage.fetch_habits_for_entry(entry["id"])
        for h in habits:
            name = h["name"]
            done = bool(h["done"])

            #Setdefualt: if key doesnt exist, create it with the defaault value 
            #equivalent to : if name not in dict: dict[name] = []
            if done:
                habit_mood_with.setdefault(name, []).append(mood)
                habit_mood_without.setdefault(name, []).append(mood)
                _ResultMixinStr []
                for name in habit_mood_with:
                    with_moods  =habit_mood_with.get(name, [])
                    without_moods = habit_mood_without.get(name, [])
                    if len(with_moods) < 2 or len(without_moods) <2:
                        continue
                    #continue skips to the next loop iteration (not enough data)
                    avg_with = sum(with_moods) / len(with_moods)
                    avg_without = sum(without_moods) / len(without_moods)
                    impact = round(avg_with - avg_without, 2)
#positive impact  for mood is higher when habit is done and negative impact is when mood is lower when habit is done
                    results.append({ 
                        "habit":       name,
                        "avg_with":     round(avg_with, 2)
                        "avg_without":  round(avg_without, 2)
                        "mood_impact" : impact'
                    } )
                    #sort by mood_impact , highest first.
                    #key = lambda x : x ["mood_impact"] -> sort criterion
                    #reverse = true for descending order
                    return results
def print_full_report() :
    """fetches all data , runs all analysis and prints a formatted report to the terminal
    this is what runs when you do : python cli.pynanalyze"""
    entries = storage.fetch_all_entries()
    if not entries:
        print("no entries yet. start logging with: python cli.py log")
        return
    print("\n" + "=" * 50)
    print("lifelog - personal insights report")
    print("=" * 50)

    #mood summaary
    # moood = get_mood_trend(entries)
    print(f"\n MOOD SUMMARY ({mood['total_entries']}entries)")
    print(f"Average : {mood['avg']}/10")
    print(f"highest : {mood['high']}/10")
    print(f"lowest : {mood['low']}/10")
    print(f"tend : {mood['trend_direction']}")

    #habit stats
    habit_stats = get_habit_stats(entries)
    print(f"\n HABIT COMPLETION")
    #visual bar : "" repeated proportionally to completion rate
    bar_len = int(s["rate"] / 10) #100% to 10 blocks 50% to 5 blocks
    bar = "❚" * bar_len + "" *(10- bar_len)
    print(f"{habits:<20} {bar}  {s['rate']}% {s['streak']}-day streak")
    # :<20 is string formatting : left align in a 20 charcter wide field
    # # this makes all habit namws align neatley in a column
     
    # mood habit correlation 
    correlations = get_mood_vs_habits_correlation(entries)
    if correlations:
        print(f"\n HABITS THAT BOOST YOUR MOOD")
        for c in correlations[:3]: #show top 3 only
            arrow = "↑" if c ["mood_impact"] > 0 else "↓"
            print(f"{c["habit"] : < 20} mood impact : {arrow} {abs(c['mood_impact'])}")
            # top words
            words = get_words_frequency(entries,  top_n=10)
            if words :
                print(f"\n TOP WORDS IN YOUR NOTES")
                word_line = "" .join(f"({w}{c})" for w, c in words)
                print(f"{word_line}")
                print("\n" + "=" * 50 + "\n")
            



    

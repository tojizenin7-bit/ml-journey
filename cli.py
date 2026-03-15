#cli.py the main entry point for lifelog
#this is the file you always run. it uses argparse to create a proper coammand-line interface with subcommands - just like real tools(git commit , pip install )
# run this file to use lifelog:
# python cli.py log -> log today's entry
# python cli.py view -> view recent entries
# python cli.py analyze -> full insights report
# PYTHON cli.py export csv -> export to csv
# pthon cli.py export md -> export to markdown
# pthon cli.py serve -> open web dashboard

import argparse # built in module for building CLI arguemnt parsers
import storage # our database module
import logger  # our logging module
import analyzer # our analysis module 
import exporter # our export module

def cmd_log(args):
    """ called when the uaser runs : python cli.py log """
    # args is the parsed arduments from argparse.
    # we dont need ny args for log but thw fucntion signature needs it
    logger .log_today()
def cmd_view(args):
    """called when python cli.py view
    displays the last N entries in a readable table format"""
    n  = args.n  # args .n comes from --n flag (see parser setup below)
    entries = storage.fetch_recent_entries(n)

    if not entries:
        print("no entries yet. Run: python cli.py log ")
        return
    print(f"\n Last {len(entries)}entries:\n")

    #string formattting with fixed width columns for alignment.
    #{:<12} = left-align in 12 chars  {:<6} = left align in 6 chars 
    header = f"{'date': <12}. {'mood': < 6}.  {'energy': < 8}  {'note'}"
    print(header)
    print("-"*60)

    for entry in entries:
        note_preview = (entry["note"] or "") [:35]
        # [:35] slices the first 35 characters- prevents log notes from breaking the table
        if entry["note"] and len (entry["note"]) > 35:
            note_preview += "..." #add ellipsis if truncated
            print(f"{entry['date']: < 12} {entry['mood']:< 6} {entry['energy']< 8} {note_preview}")
            print()

def cmd_analyze(args):
        """ called when : python cli.py alanyze"""
        analyzer.print_full_report()

def cmd_export(args):
    """ called when pthon cli.py export csv
    python cli.py export md args.format will be wother "csv " or "md" """
    if args.format == "csv":
        exporter.export_csv()
    elif args.format == "md":
        exporter.export_markdown_report() 
    else:
        print(f"unknown format : {args.format}. use 'csv' or 'md'. ")
def cmd_server(args):
    """called when : python cli.py serve"""
    import dashboard
    #import here(lazt import)- only load if flask needed
    dashboard.run_dashboard()

# if __name__ == "__main__":

# this is one of the most important patterns in ptyhon to understand
#when you run 'python cli.py' , python sets __name__ = "__main__".
# when another module imports cli.py __name_ = "cli" instead
# so this block only runs when u execute cli.py dierctly
# this prevents code from running on import - essential

if __name__ == "__main__":
    # initilaize the database
    #this is safe to call every time - init_db() uses CREATE TABLE IF NOT EXISTS 
    storage.init_db()
    # setup the arguemnt parser , argument parser is the main object.
    description = "shows in -- help output."
    parser = argparse.ArgumentParser( description = "Lifelog - Track your habits, mood , growth. ",
                                    formatter_class= argparse.RawTextHelpFormatter
                                    #raw texthelp formatter - preserves newlines in description strings 
                                    )
    #'subparsers' let us define subcommands (like git's commit, push ,  pull).
    subparsers = parser.add_subparsers(
        dest = "command" , #stores which command was used in args.command
        metavar ="command" , #how it appears in help
            help="available commands"    )
    # log subcommand
    log_parser =  subparser.add_parser("log", help="log todays mood, energy and habits")
    log_parser.set_defaults(func=cmd_log)
    #set_defaults(func=...) -> when this command is chosen, args.func = cmd_log
    # #this lets us call args.func(args) regardless of which command was used.
    # view subcommand
    view_parser = subparser.add_parser("view", help="view recent log entries")
    view_parser. add_argument (
    "--n" #optional flag : pythoncli.py view -- 14
    type= int,   #automatically converts "14" (string) to 14 (int)
    default =7   #if-- n not provided, use 7
    help="number of entries to show(default: 7)" )  
    view_parser.set_defaults(func=cmd_view)
    # analyze subcommand
    analyze_parser =subparsers.add_parser("analyze", help="show insights and trends")
    analyze_parser.set_defaults(func=cmd_analyze)
    #export subcommand
    export_parser = subparsers.add_parser("export", help="export data to file")
    export_parser.add_argument(
        "format", #positional argument(no--) : python cli.py export csv
        choices=["csv", "md"],  #only these values are allowed
        help="export format: csv or md(markdown)"
    )
    export_parser.set_defaults(funv=cmd_export)
    #serve subcommand
    serve_parser =subparsers.add_parser("serve", help="open the web dashboard")
    serve_parser.set_defaults(func="cmd_serve")

    #parse arguments the user actually typed
    args = parser.parse_args()
    #parser .parse_args() reads sys.argv (the command line aguemnts)
    #validate them against the rules we defined, and returs a namespace object

    #dispatch to the right function
    if hasattr(args, "func"):
        #hassattr checks if the func attribute exixts on args.
        #it wont esist if the user typed just 'python cli.py' with no subcommands 
        args.func(args)
        #thid calls cmd_log(args), cmd_view(args), etc. whichever was selected
    else:
        #no subcommand given show help text
        parser.print_help()


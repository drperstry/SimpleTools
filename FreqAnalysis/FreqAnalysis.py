import argparse
import textwrap

def frequency_analysis(file):
    Frequency={
    'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'g':0, 'h':0, 'i':0, 'j':0, 'k':0,
    'l':0, 'm':0, 'n':0, 'o':0, 'p':0, 'q':0, 'r':0, 's':0, 't':0, 'u':0, 'v':0,
    'w':0, 'x':0, 'y':0, 'z':0
    }
    with open(file, "r") as f:
        for line in f:
            for character in line:
                if(character.isalpha()):
                    Frequency[character.lower()] += 1
                
    
    return {k: v for k, v in sorted(Frequency.items(), key=lambda item: item[1])}

def main():
    desc=textwrap.dedent('''FreqAnalysis:

            usage: 
                1: FreqAnalysis.py Analyze [-h] --Input input.txt''')
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    Analyze=subparser.add_parser('Analyze')


    Analyze.add_argument("--inputfile", '-I',type=str, help="--input.txt, ...", required=True)

    args = parser.parse_args()
    if args.Command == None:
        print("choose command Analyze")
    elif args.Command == 'Analyze':
        print(frequency_analysis(args.inputfile))

# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()
def find_line(word):
    state = False
    line_no = 1
    with open("yahya.txt") as f:
        while True:
            data = f.readline()
            
            if not data:
                if state == False:
                    print("Not Found")
                    break
                else:
                    break 
                
            if word in data:
                print(f"Found in Line: {line_no}") 
                state = True
            line_no += 1  

def main():
    target_word = input("Enter the word to search for: ")
    
    find_line(target_word)
main()
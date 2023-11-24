import ast

def format_json_answer(s: str) -> str:
    """
    If a string contains "```json" and "```", remove them and return the stuff at the middle fo them, 
    else return the string itself

    Parameters:
    a (str): the input string containing a JSON of interest

    Returns:
    str: JSON as a string
    """
    start_tag = "```json"
    end_tag = "```"

    if start_tag in s and end_tag in s:
        s = s[s.index(start_tag) + len(start_tag): s.rindex(end_tag)]

    # remove all the line breaks
    s = s.replace("\n", "")
    
    new_s = ""
    for i in range(0, len(s)):
        if s[i] == "\'":
            is_quote_inside_value = True
            j = i + 1
            while j < len(s):
                if s[j] == " ":
                    j += 1
                else:
                    if s[j] == "\\" or s[j] == "," or s[j] == ":" or s[j] == "{" or s[j] == "}" or s[j] == "[" or s[j] == "]":
                        is_quote_inside_value = False
                    break
            j = i - 1
            if is_quote_inside_value:
                while j >= 0:

                    if s[j] == " ":
                        j -= 1
                    else:
                        if s[j] == "\\" or s[j] == "," or s[j] == ":" or s[j] == "{" or s[j] == "}" or s[j] == "[" or s[j] == "]":
                            is_quote_inside_value = False
                        break
            if is_quote_inside_value:
                new_s += "\\\'"
            else:
                new_s += "\'"
            
        elif s[i] == "\"":
            is_quote_inside_value = True
            j = i + 1
            while j < len(s):
                if s[j] == " ":
                    j += 1
                else:
                    if s[j] == "," or s[j] == ":" or s[j] == "{" or s[j] == "}" or s[j] == "[" or s[j] == "]":
                        is_quote_inside_value = False
                    break
            j = i - 1
            if is_quote_inside_value:
                while j >= 0:
                    if s[j] == " ":
                        j -= 1
                    else:
                        if s[j] == "," or s[j] == ":" or s[j] == "{" or s[j] == "}" or s[j] == "[" or s[j] == "]":
                            is_quote_inside_value = False
                        break
            if is_quote_inside_value:
                new_s += "\\\""
            else:
                new_s += "\""
            
        else:
            new_s += s[i]
    return new_s

    
str = "{'description': 'Arthur Conan Doyle is the creator of Sherlock Holmes',\n 'source': 'Arthur Conan Doyle, a famous British author, known for Arthur Conan Doyle\\\'s detective novels featuring Sherlock Holmes, was born in Edinburgh but spent considerable time in London.'}"
print(str)
print(format_json_answer(str))
obj = ast.literal_eval(format_json_answer(str))
print(obj)

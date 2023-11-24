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
      if s[i] == "\'" and i < len(s) - 2 and i > 2 and s[i-2] != "," and s[i+1] != "," and s[i-2] != ":" and s[i+1] != ":":
         print(s[i])
         new_s += "\\\'"
      elif s[i] == "\"" and i < len(s) - 2 and i > 2 and s[i-2] != "," and s[i+1] != "," and s[i-2] != ":" and s[i+1] != ":":
         new_s += "\\\""
      else:
         new_s += s[i]
   return new_s


str = " {'description': 'Arthur Conan Doyle inspired Agatha Christie',\n 'source': 'Arthur Conan Doyle\'s Sherlock Holmes, a character with incredible deductive reasoning skills, went onto inspire Agatha Christie\'s character Hercule Poirot.'}"
print(format_json_answer(str))
obj = ast.literal_eval(format_json_answer(str))
print(obj)

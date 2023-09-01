let format_variable value =
  match value with
  | `Int i -> string_of_int i
  | `String s -> "\"" ^ s ^ "\""
  | `Function -> "<fun>"
  (* Add more cases for other types as needed *)

let print_variables variables =
  let formatted_vars =
    List.map (fun (var, value) -> var ^ " -> " ^ (format_variable value)) variables
  in
  let formatted_string = "{ " ^ String.concat ", " formatted_vars ^ " }" in
  print_endline formatted_string

(* Example usage *)
let a = `Int 5
let c = `Int 12
let f = `Function







let a = 5;;
let c = 7 + a;;
let f y = y + c;;




let variables = [
  ("a", a);
  ("c", c);
  ("f", f);
]

print_variables variables

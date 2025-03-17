import argparse
import pyperclip
import re

def remove_non_digits(input_string: str) -> str:
    """Remove qualquer caractere que não seja um dígito da string."""
    return re.sub(r'\D', '', input_string)

def main():
    parser = argparse.ArgumentParser(description="Remove caracteres não numéricos de uma string.")
    parser.add_argument("input_string", type=str, nargs='?', help="String de entrada", default=None)
    parser.add_argument("-c", "--clipboard", action="store_true", help="Usar o conteúdo do clipboard como entrada")
    parser.add_argument("-o", "--output-clipboard", action="store_true", help="Copiar o resultado para o clipboard")
    args = parser.parse_args()
    
    if args.clipboard:
        args.input_string = pyperclip.paste()
    
    if args.input_string is None:
        print("Erro: Nenhuma string fornecida.")
        return
    
    result = remove_non_digits(args.input_string)
    
    if args.output_clipboard:
        pyperclip.copy(result)
        print(f"Resultado copiado para o clipboard: {result}")
    else:
        print(result)

if __name__ == "__main__":
    main()
